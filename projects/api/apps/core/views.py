from rest_framework import viewsets
from rest_framework.permissions import AllowAny  # replace with your auth later

from .models import (
    Project,
    Dimension,
    Unit,
    Taxonomy,
    Term,
    ConservedEntity,
    TransformableEntity,
    Good,
    TransformableEntityContainConservedEntity,
    GoodContainTransformableEntity,
    GoodContainGood,
    Process,
    EconomicFlow,
    ElementaryFlowCompartment,
    ElementaryFlow,
)

from .serializers import (
    ProjectSerializer,
    DimensionSerializer,
    UnitSerializer,
    TaxonomySerializer,
    TermSerializer,
    ConservedEntitySerializer,
    TransformableEntitySerializer,
    GoodSerializer,
    TransformableEntityContainConservedEntitySerializer,
    GoodContainTransformableEntitySerializer,
    GoodContainGoodSerializer,
    ProcessSerializer,
    EconomicFlowSerializer,
    ElementaryFlowCompartmentSerializer,
    ElementaryFlowSerializer,
)


class ProjectFilterMixin:
    # Adds simple project scoping:
    #   - /resource/?project=<project_id>
    #
    # Set `project_filter_field` to the Django ORM path to the project FK,
    # e.g. "project" or "dimension__project" or "process__project".
    project_filter_field = None  # override in subclasses

    def get_queryset(self):
        qs = super().get_queryset()
        project_id = self.request.query_params.get("project")
        if project_id and self.project_filter_field:
            return qs.filter(**{self.project_filter_field: project_id})
        return qs


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all().order_by("id")
    serializer_class = ProjectSerializer
    permission_classes = [AllowAny]


class DimensionViewSet(ProjectFilterMixin, viewsets.ModelViewSet):
    queryset = Dimension.objects.select_related("project").all().order_by("id")
    serializer_class = DimensionSerializer
    permission_classes = [AllowAny]
    project_filter_field = "project"


class UnitViewSet(ProjectFilterMixin, viewsets.ModelViewSet):
    queryset = (
        Unit.objects.select_related("dimension", "dimension__project")
        .all()
        .order_by("id")
    )
    serializer_class = UnitSerializer
    permission_classes = [AllowAny]
    project_filter_field = "dimension__project"


class TaxonomyViewSet(viewsets.ModelViewSet):
    queryset = Taxonomy.objects.all().order_by("id")
    serializer_class = TaxonomySerializer
    permission_classes = [AllowAny]


class TermViewSet(viewsets.ModelViewSet):
    queryset = Term.objects.select_related("taxonomy").all().order_by("id")
    serializer_class = TermSerializer
    permission_classes = [AllowAny]


class ConservedEntityViewSet(ProjectFilterMixin, viewsets.ModelViewSet):
    queryset = (
        ConservedEntity.objects.select_related("project")
        .prefetch_related("terms")
        .all()
        .order_by("id")
    )
    serializer_class = ConservedEntitySerializer
    permission_classes = [AllowAny]
    project_filter_field = "project"


class TransformableEntityViewSet(ProjectFilterMixin, viewsets.ModelViewSet):
    queryset = (
        TransformableEntity.objects.select_related("project")
        .prefetch_related("terms")
        .all()
        .order_by("id")
    )
    serializer_class = TransformableEntitySerializer
    permission_classes = [AllowAny]
    project_filter_field = "project"


class GoodViewSet(ProjectFilterMixin, viewsets.ModelViewSet):
    queryset = (
        Good.objects.select_related(
            "project", "reference_unit", "reference_unit__dimension"
        )
        .prefetch_related("terms")
        .all()
        .order_by("id")
    )
    serializer_class = GoodSerializer
    permission_classes = [AllowAny]
    project_filter_field = "project"


class TransformableEntityContainConservedEntityViewSet(
    ProjectFilterMixin, viewsets.ModelViewSet
):
    queryset = (
        TransformableEntityContainConservedEntity.objects.select_related(
            "unit",
            "conserved_entity",
            "conserved_entity__project",
            "transformable_entity",
            "transformable_entity__project",
        )
        .all()
        .order_by("id")
    )
    serializer_class = TransformableEntityContainConservedEntitySerializer
    permission_classes = [AllowAny]
    # either side ties to a project; enforce scoping via conserved_entity.project
    project_filter_field = "conserved_entity__project"


class GoodContainTransformableEntityViewSet(ProjectFilterMixin, viewsets.ModelViewSet):
    queryset = (
        GoodContainTransformableEntity.objects.select_related(
            "unit",
            "good",
            "good__project",
            "transformable_entity",
            "transformable_entity__project",
        )
        .all()
        .order_by("id")
    )
    serializer_class = GoodContainTransformableEntitySerializer
    permission_classes = [AllowAny]
    project_filter_field = "good__project"


class GoodContainGoodViewSet(ProjectFilterMixin, viewsets.ModelViewSet):
    queryset = (
        GoodContainGood.objects.select_related(
            "unit",
            "parent_good",
            "parent_good__project",
            "child_good",
            "child_good__project",
        )
        .all()
        .order_by("id")
    )
    serializer_class = GoodContainGoodSerializer
    permission_classes = [AllowAny]
    project_filter_field = "parent_good__project"


class ProcessViewSet(ProjectFilterMixin, viewsets.ModelViewSet):
    queryset = Process.objects.select_related("project").all().order_by("id")
    serializer_class = ProcessSerializer
    permission_classes = [AllowAny]
    project_filter_field = "project"


class EconomicFlowViewSet(ProjectFilterMixin, viewsets.ModelViewSet):
    queryset = (
        EconomicFlow.objects.select_related(
            "process", "process__project", "good", "good__project", "unit"
        )
        .all()
        .order_by("id")
    )
    serializer_class = EconomicFlowSerializer
    permission_classes = [AllowAny]
    project_filter_field = "process__project"


class ElementaryFlowCompartmentViewSet(ProjectFilterMixin, viewsets.ModelViewSet):
    queryset = (
        ElementaryFlowCompartment.objects.select_related(
            "project", "parent_compartment"
        )
        .all()
        .order_by("id")
    )
    serializer_class = ElementaryFlowCompartmentSerializer
    permission_classes = [AllowAny]
    project_filter_field = "project"


class ElementaryFlowViewSet(ProjectFilterMixin, viewsets.ModelViewSet):
    queryset = (
        ElementaryFlow.objects.select_related(
            "process",
            "process__project",
            "compartment",
            "compartment__project",
            "conserved_entity",
            "conserved_entity__project",
            "unit",
        )
        .all()
        .order_by("id")
    )
    serializer_class = ElementaryFlowSerializer
    permission_classes = [AllowAny]
    project_filter_field = "process__project"
