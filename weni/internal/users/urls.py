from rest_framework import routers
from rest_framework_nested.routers import NestedSimpleRouter

from weni.internal.users.views import UserViewSet, UserEndpoint, UserPermissionEndpoint


router = routers.DefaultRouter()
router.register(r"users", UserViewSet, basename="users")

flows_router = routers.SimpleRouter()
flows_router.register("flows-users", UserEndpoint, basename="flows_users")

user_permission_router = NestedSimpleRouter(flows_router, "flows-users", lookup="user")
user_permission_router.register("permission", UserPermissionEndpoint, basename="flows_users.permission")

urlpatterns = router.urls
urlpatterns += flows_router.urls
urlpatterns += user_permission_router.urls
