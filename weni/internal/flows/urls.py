from rest_framework import routers

from weni.internal.flows.views import FlowViewSet


router = routers.DefaultRouter()
router.register(r"flows", FlowViewSet, basename="flows")


urlpatterns = router.urls
