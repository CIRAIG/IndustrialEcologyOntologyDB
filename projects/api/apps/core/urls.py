from rest_framework.routers import DefaultRouter
from .views import (
    ProjectViewSet,
    DimensionViewSet,
    UnitViewSet,
    TaxonomyViewSet,
    TermViewSet,
    ConservedEntityViewSet,
    TransformableEntityViewSet,
    GoodViewSet,
    TransformableEntityContainConservedEntityViewSet,
    GoodContainTransformableEntityViewSet,
    GoodContainGoodViewSet,
    ProcessViewSet,
    EconomicFlowViewSet,
    ElementaryFlowCompartmentViewSet,
    ElementaryFlowViewSet,
)

router = DefaultRouter()
router.register(r"projects", ProjectViewSet)
router.register(r"dimensions", DimensionViewSet)
router.register(r"units", UnitViewSet)
router.register(r"taxonomies", TaxonomyViewSet)
router.register(r"terms", TermViewSet)

router.register(r"conserved-entities", ConservedEntityViewSet)
router.register(r"transformable-entities", TransformableEntityViewSet)
router.register(r"goods", GoodViewSet)

router.register(r"te-contain-ce", TransformableEntityContainConservedEntityViewSet)
router.register(r"good-contain-te", GoodContainTransformableEntityViewSet)
router.register(r"good-contain-good", GoodContainGoodViewSet)

router.register(r"processes", ProcessViewSet)
router.register(r"economic-flows", EconomicFlowViewSet)
router.register(r"elementary-flow-compartments", ElementaryFlowCompartmentViewSet)
router.register(r"elementary-flows", ElementaryFlowViewSet)

urlpatterns = router.urls
