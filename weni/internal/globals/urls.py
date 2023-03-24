from rest_framework_nested import routers

from weni.internal.globals.views import GlobalViewSet


router = routers.SimpleRouter()
router.register(r"globals", GlobalViewSet, basename="global")

urlpatterns = router.urls
