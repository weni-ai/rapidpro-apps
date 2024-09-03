from rest_framework_nested import routers

from weni.internal.globals.views import GlobalRetailViewSet, GlobalViewSet


router = routers.SimpleRouter()
router.register(r"globals", GlobalViewSet, basename="global")
router.register(r"globals_retail", GlobalRetailViewSet, basename="global_retail")

urlpatterns = router.urls
