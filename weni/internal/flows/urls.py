from rest_framework import routers

from weni.internal.flows.views import FlowViewSet, ProjectFlowsViewSet


router = routers.DefaultRouter()
router.register(r"flows", FlowViewSet, basename="flows")

router.register(r"project-flows", ProjectFlowsViewSet, basename="project-flows")

urlpatterns = router.urls
