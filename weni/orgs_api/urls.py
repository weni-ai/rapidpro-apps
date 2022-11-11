from rest_framework import routers
from .views import OrgViewSet

router = routers.DefaultRouter()
router.register(r"org", OrgViewSet, basename="org")

urlpatterns = router.urls
