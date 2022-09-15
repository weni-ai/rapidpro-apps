from rest_framework import routers

from weni.internal.users.views import UserViewSet


router = routers.DefaultRouter()
router.register(r"users", UserViewSet, basename="users")


urlpatterns = router.urls
