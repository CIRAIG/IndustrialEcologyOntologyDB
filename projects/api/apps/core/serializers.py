from rest_framework import serializers

from .models import (
    Project,
    Unit,
    Dimension,
    Term,
    Taxonomy,
    Good,
    ConservedEntity,
    TransformableEntity,
    TransformableEntityContainConservedEntity,
    GoodContainTransformableEntity,
    GoodContainGood,
    Process,
    EconomicFlow,
    ElementaryFlowCompartment,
    ElementaryFlow,
)


class ProjectConsistencySerializerMixin:
    # Helper to validate "all linked objects belong to the same project".
    #
    # Works for both create and update/partial_update by looking at:
    # - incoming attrs
    # - or existing instance values when attrs doesn't include the field

    def _obj(self, attrs, field_name):
        if field_name in attrs:
            return attrs[field_name]
        if getattr(self, "instance", None) is not None:
            return getattr(self.instance, field_name, None)
        return None

    def _unit_project(self, unit: Unit | None):
        if not unit:
            return None
        # Unit -> Dimension -> Project
        dim = getattr(unit, "dimension", None)
        return getattr(dim, "project", None)

    def _require_same_project(self, *, expected_project, checks: dict):
        # checks: dict[label -> (project, field_name_for_error)]
        errors = {}
        for label, (proj, field_name) in checks.items():
            if proj is None:
                continue
            if expected_project is not None and proj != expected_project:
                errors[field_name] = (
                    f"{label} belongs to a different project "
                    f"(expected project_id={expected_project.id}, got project_id={proj.id})."
                )
        if errors:
            raise serializers.ValidationError(errors)


class ProjectSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Project
        fields = ["id", "url", "name", "description", "created_at", "updated_at"]
        read_only_fields = ["id", "url", "created_at", "updated_at"]


class DimensionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Dimension
        fields = ["id", "url", "project", "name", "description"]
        read_only_fields = ["id", "url"]


class UnitSerializer(serializers.HyperlinkedModelSerializer):
    # Optional: show dimension name read-only (convenient for UI)
    dimension_name = serializers.CharField(source="dimension.name", read_only=True)

    class Meta:
        model = Unit
        fields = ["id", "url", "name", "symbol", "dimension", "dimension_name"]
        read_only_fields = ["id", "url", "dimension_name"]


class TaxonomySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Taxonomy
        fields = ["id", "url", "name", "description"]
        read_only_fields = ["id", "url"]


class TermSerializer(serializers.HyperlinkedModelSerializer):
    taxonomy_name = serializers.CharField(source="taxonomy.name", read_only=True)

    class Meta:
        model = Term
        fields = ["id", "url", "taxonomy", "taxonomy_name", "name", "description"]
        read_only_fields = ["id", "taxonomy_name"]


class ProcessSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Process
        fields = ["id", "url", "project", "name", "description"]
        read_only_fields = ["id", "url"]


class ElementaryFlowCompartmentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ElementaryFlowCompartment
        fields = ["id", "url", "project", "name", "description", "parent_compartment"]
        read_only_fields = ["id", "url"]


class TermMixinSerializer(serializers.HyperlinkedModelSerializer):
    # For models that have `terms = ManyToManyField(Term, ...)`.
    # Write by IDs, optionally expose term objects in `terms_detail` read-only.
    terms = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Term.objects.all(),
        required=False,
    )
    terms_detail = TermSerializer(source="terms", many=True, read_only=True)

    class Meta:
        abstract = True


class ConservedEntitySerializer(TermMixinSerializer):
    class Meta:
        model = ConservedEntity
        fields = [
            "id",
            "url",
            "project",
            "name",
            "short_name",
            "molar_mass",
            "terms",
            "terms_detail",
        ]
        read_only_fields = ["id", "url"]


class TransformableEntitySerializer(TermMixinSerializer):
    class Meta:
        model = TransformableEntity
        fields = ["id", "url", "project", "name", "short_name", "terms", "terms_detail"]
        read_only_fields = ["id", "url"]


class GoodSerializer(
    ProjectConsistencySerializerMixin, serializers.HyperlinkedModelSerializer
):
    # ... keep your existing fields (terms, terms_detail, reference_unit_detail, etc.)

    def validate(self, attrs):
        attrs = super().validate(attrs)
        good_project = self._obj(attrs, "project")
        reference_unit = self._obj(attrs, "reference_unit")

        unit_project = self._unit_project(reference_unit)

        # Reference unit must be from same project as the Good.
        self._require_same_project(
            expected_project=good_project,
            checks={
                "reference_unit.dimension.project": (unit_project, "reference_unit"),
            },
        )
        return attrs

    class Meta:
        model = Good
        fields = [
            "id",
            "url",
            "project",
            "name",
            "description",
            "reference_unit",
            # keep your existing read-only / nested fields if you had them
            # "reference_unit_detail",
            # "terms", "terms_detail",
        ]
        read_only_fields = ["id", "url"]


class TransformableEntityContainConservedEntitySerializer(
    ProjectConsistencySerializerMixin, serializers.HyperlinkedModelSerializer
):
    def validate(self, attrs):
        attrs = super().validate(attrs)

        conserved = self._obj(attrs, "conserved_entity")
        transformable = self._obj(attrs, "transformable_entity")
        unit = self._obj(attrs, "unit")

        conserved_project = getattr(conserved, "project", None)
        transformable_project = getattr(transformable, "project", None)
        unit_project = self._unit_project(unit)

        # Choose an "expected" project from whichever side is present.
        expected = conserved_project or transformable_project

        self._require_same_project(
            expected_project=expected,
            checks={
                "transformable_entity.project": (
                    transformable_project,
                    "transformable_entity",
                ),
                "unit.dimension.project": (unit_project, "unit"),
            },
        )
        return attrs

    class Meta:
        model = TransformableEntityContainConservedEntity
        fields = [
            "id",
            "url",
            "conserved_entity",
            "transformable_entity",
            "unit",
            "ratio",
        ]
        read_only_fields = ["id", "url"]


class GoodContainTransformableEntitySerializer(
    ProjectConsistencySerializerMixin, serializers.HyperlinkedModelSerializer
):
    def validate(self, attrs):
        attrs = super().validate(attrs)

        good = self._obj(attrs, "good")
        transformable = self._obj(attrs, "transformable_entity")
        unit = self._obj(attrs, "unit")

        good_project = getattr(good, "project", None)
        transformable_project = getattr(transformable, "project", None)
        unit_project = self._unit_project(unit)

        expected = good_project or transformable_project

        self._require_same_project(
            expected_project=expected,
            checks={
                "transformable_entity.project": (
                    transformable_project,
                    "transformable_entity",
                ),
                "unit.dimension.project": (unit_project, "unit"),
            },
        )
        return attrs

    class Meta:
        model = GoodContainTransformableEntity
        fields = ["id", "url", "good", "transformable_entity", "quantity", "unit"]
        read_only_fields = ["id", "url"]


class GoodContainGoodSerializer(
    ProjectConsistencySerializerMixin, serializers.HyperlinkedModelSerializer
):
    def validate(self, attrs):
        attrs = super().validate(attrs)

        parent = self._obj(attrs, "parent_good")
        child = self._obj(attrs, "child_good")
        unit = self._obj(attrs, "unit")

        parent_project = getattr(parent, "project", None)
        child_project = getattr(child, "project", None)
        unit_project = self._unit_project(unit)

        expected = parent_project or child_project

        self._require_same_project(
            expected_project=expected,
            checks={
                "child_good.project": (child_project, "child_good"),
                "unit.dimension.project": (unit_project, "unit"),
            },
        )
        return attrs

    class Meta:
        model = GoodContainGood
        fields = ["id", "url", "parent_good", "child_good", "quantity", "unit"]
        read_only_fields = ["id", "url"]


class EconomicFlowSerializer(
    ProjectConsistencySerializerMixin, serializers.HyperlinkedModelSerializer
):
    def validate(self, attrs):
        attrs = super().validate(attrs)

        process = self._obj(attrs, "process")
        good = self._obj(attrs, "good")
        unit = self._obj(attrs, "unit")

        process_project = getattr(process, "project", None)
        good_project = getattr(good, "project", None)
        unit_project = self._unit_project(unit)

        expected = process_project or good_project

        self._require_same_project(
            expected_project=expected,
            checks={
                "good.project": (good_project, "good"),
                "unit.dimension.project": (unit_project, "unit"),
            },
        )
        return attrs

    class Meta:
        model = EconomicFlow
        fields = [
            "id",
            "url",
            "process",
            "good",
            "quantity",
            "unit",
            "direction",
            "is_byproduct",
        ]
        read_only_fields = ["id", "url"]


class ElementaryFlowSerializer(
    ProjectConsistencySerializerMixin, serializers.HyperlinkedModelSerializer
):
    def validate(self, attrs):
        attrs = super().validate(attrs)

        process = self._obj(attrs, "process")
        compartment = self._obj(attrs, "compartment")
        conserved = self._obj(attrs, "conserved_entity")
        unit = self._obj(attrs, "unit")

        process_project = getattr(process, "project", None)
        compartment_project = getattr(compartment, "project", None)
        conserved_project = getattr(conserved, "project", None)
        unit_project = self._unit_project(unit)

        expected = process_project or compartment_project or conserved_project

        self._require_same_project(
            expected_project=expected,
            checks={
                "compartment.project": (compartment_project, "compartment"),
                "conserved_entity.project": (conserved_project, "conserved_entity"),
                "unit.dimension.project": (unit_project, "unit"),
            },
        )
        return attrs

    class Meta:
        model = ElementaryFlow
        fields = [
            "id",
            "url",
            "process",
            "compartment",
            "conserved_entity",
            "quantity",
            "unit",
            "direction",
        ]
        read_only_fields = ["id", "url"]
