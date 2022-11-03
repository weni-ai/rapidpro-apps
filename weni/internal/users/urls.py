from django.urls import path

from rest_framework import routers

from weni.internal.users.views import UserViewSet, UserEndpoint, UserPermissionEndpoint


router = routers.DefaultRouter()
router.register(r"users", UserViewSet, basename="users")

flows_router = [
    path(
        "flows-users/", UserEndpoint.as_view({"get": "retrieve", "patch": "partial_update"}), name="flow_users-detail"
    ),
]

user_permission_router = [
    path(
        "user-permission/",
        UserPermissionEndpoint.as_view({"get": "retrieve", "patch": "partial_update", "delete": "destroy"}),
        name="user_permission",
    ),
]

urlpatterns = router.urls
urlpatterns += flows_router
urlpatterns += user_permission_router
