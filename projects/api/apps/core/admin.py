from django.contrib import admin
from admin_auto_filters.filters import AutocompleteFilterFactory
from import_export.admin import ImportExportModelAdmin
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
    ProductionFactor,
    ProductionFactorContainTransformableEntity,
    ElementaryFlowType,
    ElementaryFlow,
)


@admin.register(Project)
class ProjectAdmin(ImportExportModelAdmin):
    list_display = ("name", "description", "created_at", "updated_at")
    search_fields = ("name",)


@admin.register(Dimension)
class DimensionAdmin(ImportExportModelAdmin):
    list_display = ("name", "description", "project")
    search_fields = ("name",)
    list_filter = (AutocompleteFilterFactory("project", "project"),)


@admin.register(Unit)
class UnitAdmin(ImportExportModelAdmin):
    list_display = ("name", "symbol", "dimension")
    search_fields = ("name", "symbol")
    list_filter = ("dimension",)


@admin.register(Taxonomy)
class TaxonomyAdmin(ImportExportModelAdmin):
    list_display = ("name", "description")
    search_fields = ("name",)


@admin.register(Term)
class TermAdmin(ImportExportModelAdmin):
    list_display = ("name", "taxonomy", "description")
    search_fields = ("name",)
    list_filter = ("taxonomy",)


@admin.register(ConservedEntity)
class ConservedEntityAdmin(ImportExportModelAdmin):
    list_display = ("name", "short_name", "molar_mass", "project")
    search_fields = ("name",)
    filter_horizontal = ("terms",)
    list_filter = (AutocompleteFilterFactory("project", "project"),)


@admin.register(TransformableEntity)
class TransformableEntityAdmin(ImportExportModelAdmin):
    list_display = ("name", "short_name", "project")
    search_fields = ("name",)
    filter_horizontal = ("terms",)
    list_filter = (AutocompleteFilterFactory("project", "project"),)


@admin.register(Good)
class GoodAdmin(ImportExportModelAdmin):
    list_display = ("name", "description", "reference_unit", "project")
    search_fields = ("name",)
    filter_horizontal = ("terms",)
    list_filter = (
        AutocompleteFilterFactory("project", "project"),
        "reference_unit",
        "reference_unit__dimension",
    )


@admin.register(TransformableEntityContainConservedEntity)
class TransformableEntityContainConservedEntityAdmin(ImportExportModelAdmin):
    list_display = ("transformable_entity", "conserved_entity", "ratio", "unit")
    search_fields = ("transformable_entity__name", "conserved_entity__name")
    list_filter = (
        AutocompleteFilterFactory("transformable entity", "transformable_entity"),
        AutocompleteFilterFactory("conserved entity", "conserved_entity"),
        "unit",
        "unit__dimension",
    )
    autocomplete_fields = ["transformable_entity", "conserved_entity", "unit"]


@admin.register(GoodContainTransformableEntity)
class GoodContainTransformableEntityAdmin(ImportExportModelAdmin):
    list_display = (
        "good__name",
        "transformable_entity",
        "quantity",
        "unit",
        "good__project",
    )
    search_fields = ("good__name", "transformable_entity__name")
    list_filter = (
        AutocompleteFilterFactory("project", "good__project"),
        AutocompleteFilterFactory("good", "good"),
        AutocompleteFilterFactory("transformable entity", "transformable_entity"),
        "unit",
        "unit__dimension",
    )


@admin.register(GoodContainGood)
class GoodContainGoodAdmin(ImportExportModelAdmin):
    list_display = (
        "parent_good__name",
        "child_good__name",
        "quantity",
        "unit",
        "parent_good__project",
    )
    search_fields = ("parent_good__name", "child_good__name")
    list_filter = (
        AutocompleteFilterFactory("project", "parent_good__project"),
        AutocompleteFilterFactory("parent good", "parent_good"),
        AutocompleteFilterFactory("child good", "child_good"),
        "unit",
        "unit__dimension",
    )


@admin.register(Process)
class ProcessAdmin(ImportExportModelAdmin):
    list_display = ("name", "description", "project")
    search_fields = ("name",)
    list_filter = (AutocompleteFilterFactory("project", "project"),)


@admin.register(EconomicFlow)
class EconomicFlowAdmin(ImportExportModelAdmin):
    list_display = (
        "process",
        "good__name",
        "quantity",
        "unit",
        "direction",
        "is_byproduct",
        "process__project",
    )
    search_fields = ("name",)
    list_filter = (
        AutocompleteFilterFactory("project", "process__project"),
        AutocompleteFilterFactory("process", "process"),
        AutocompleteFilterFactory("good", "good"),
        "direction",
        "is_byproduct",
        "unit",
        "unit__dimension",
    )


@admin.register(ElementaryFlowCompartment)
class ElementaryFlowCompartmentAdmin(ImportExportModelAdmin):
    list_display = ("name", "description", "parent_compartment", "project")
    search_fields = ("name",)
    list_filter = (
        AutocompleteFilterFactory("project", "project"),
        AutocompleteFilterFactory("parent compartment", "parent_compartment"),
    )


@admin.register(ProductionFactor)
class ProductionFactorAdmin(ImportExportModelAdmin):
    list_display = ("name", "project")
    search_fields = ("name",)
    list_filter = (AutocompleteFilterFactory("project", "project"),)


@admin.register(ProductionFactorContainTransformableEntity)
class ProductionFactorContainTransformableEntityAdmin(ImportExportModelAdmin):
    list_display = (
        "production_factor",
        "transformable_entity",
        "quantity",
        "unit",
        "production_factor__project",
    )
    list_filter = (
        AutocompleteFilterFactory("project", "production_factor__project"),
        AutocompleteFilterFactory("production factor", "production_factor"),
        AutocompleteFilterFactory("transformable entity", "transformable_entity"),
        "unit",
        "unit__dimension",
    )
    autocomplete_fields = [
        "production_factor",
        "transformable_entity",
        "unit",
    ]


@admin.register(ElementaryFlowType)
class ElementaryFlowTypeAdmin(ImportExportModelAdmin):
    list_display = (
        "production_factor",
        "compartment",
        "production_factor__project",
    )
    search_fields = (
        "production_factor__name",
        "compartment__name",
    )
    list_filter = (
        AutocompleteFilterFactory("project", "production_factor__project"),
        AutocompleteFilterFactory("production factor", "production_factor"),
        AutocompleteFilterFactory("compartment", "compartment"),
    )
    autocomplete_fields = (
        "production_factor",
        "compartment",
    )


@admin.register(ElementaryFlow)
class ElementaryFlowAdmin(ImportExportModelAdmin):
    list_display = (
        "elementary_flow_type",
        "process",
        "quantity",
        "unit",
        "direction",
        "elementary_flow_type__production_factor__project",
    )
    list_filter = (
        AutocompleteFilterFactory(
            "project", "elementary_flow_type__production_factor__project"
        ),
        AutocompleteFilterFactory("elementary flow type", "elementary_flow_type"),
        AutocompleteFilterFactory("process", "process"),
        AutocompleteFilterFactory(
            "production factor", "elementary_flow_type__production_factor"
        ),
        AutocompleteFilterFactory("compartment", "elementary_flow_type__compartment"),
        "direction",
        "unit",
        "unit__dimension",
    )
    autocomplete_fields = [
        "elementary_flow_type",
        "process",
        "unit",
    ]
