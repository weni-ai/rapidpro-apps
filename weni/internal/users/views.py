from typing import TYPE_CHECKING

from django.conf import settings
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import exceptions
from rest_framework import mixins
from rest_framework.exceptions import ValidationError

from weni.internal.views import InternalGenericViewSet
from weni.internal.users.serializers import (
    UserAPITokenSerializer,
    UserSerializer,
    UserPermissionSerializer,
)
from temba.api.models import APIToken
from temba.orgs.models import Org


if TYPE_CHECKING:
    from rest_framework.request import Request

User = get_user_model()


class UserViewSet(InternalGenericViewSet):
    @action(
        detail=False,
        methods=["GET"],
        url_path="api-token",
        serializer_class=UserAPITokenSerializer,
    )
    def api_token(self, request: "Request", **kwargs):
        serializer = self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data.get("user")
        project = serializer.validated_data.get("project")

        try:
            api_token = APIToken.objects.get(user=user, org=project.org)
        except APIToken.DoesNotExist:
            raise exceptions.PermissionDenied()

        return Response(
            dict(
                user=api_token.user.email,
                project=project.project_uuid,
                api_token=api_token.key,
            )
        )


class UserPermissionEndpoint(InternalGenericViewSet):
    serializer_class = UserPermissionSerializer

    def retrieve(self, request):
        org = get_object_or_404(Org, uuid=request.query_params.get("org_uuid"))
        user = get_object_or_404(
            User,
            email=request.query_params.get("user_email"),
            is_active=request.query_params.get("is_active", True),
        )

        permissions = self._get_user_permissions(org, user)
        serializer = self.get_serializer(permissions)

        return Response(serializer.data)

    def partial_update(self, request):
        org = get_object_or_404(Org, uuid=request.data.get("org_uuid"))
        user, created = User.objects.get_or_create(
            email=request.data.get("user_email"),
            defaults={"username": request.data.get("user_email")},
            is_active=request.query_params.get("is_active", True),
        )

        self._validate_permission(org, request.data.get("permission", ""))
        self._set_user_permission(org, user, request.data.get("permission", ""))

        permissions = self._get_user_permissions(org, user)
        serializer = self.get_serializer(permissions)

        return Response(serializer.data)

    def destroy(self, request):
        org = get_object_or_404(Org, uuid=request.data.get("org_uuid"))
        user = get_object_or_404(
            User,
            email=request.data.get("user_email"),
            is_active=request.query_params.get("is_active", True),
        )

        self._validate_permission(org, request.data.get("permission", ""))
        self._remove_user_permission(org, user, request.data.get("permission", ""))

        permissions = self._get_user_permissions(org, user)
        serializer = self.get_serializer(permissions)

        return Response(serializer.data)

    def _remove_user_permission(self, org: Org, user: User, permission: str):
        permissions = self._get_permissions(org)
        permissions.get(permission).remove(user)

    def _set_user_permission(self, org: Org, user: User, permission: str):
        permissions = self._get_permissions(org)

        for perm_name, org_field in permissions.items():
            if not perm_name == permission:
                org_field.remove(user)

        permissions.get(permission).add(user)

    def _validate_permission(self, org: Org, permission: str):
        permissions_keys = self._get_permissions(org).keys()
        if permission not in permissions_keys:
            raise ValidationError(detail=f"{permission} is not a valid permission!")

    def _get_permissions(self, org: Org) -> dict:
        return {
            "administrator": org.administrators,
            "viewer": org.viewers,
            "editor": org.editors,
            "surveyor": org.surveyors,
            "agent": org.agents,
        }

    def _get_user_permissions(self, org: Org, user: User) -> dict:
        permissions = {}
        org_permissions = self._get_permissions(org)

        for perm_name, org_field in org_permissions.items():
            if org_field.filter(pk=user.id).exists():
                permissions[perm_name] = True

        return permissions


class UserEndpoint(InternalGenericViewSet, mixins.RetrieveModelMixin):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    lookup_field = "uuid"

    def partial_update(self, request):
        instance = get_object_or_404(User, email=request.query_params.get("email"))

        if request.data.get("language") not in [language[0] for language in settings.LANGUAGES]:
            raise ValidationError("Invalid argument: language")

        user_settings = instance.get_settings()
        user_settings.language = request.data.get("language")
        user_settings.save()

        return Response(status=status.HTTP_200_OK)

    def retrieve(self, request):
        if not request.query_params.get("email"):
            raise ValidationError(detail="empty email")

        user = User.objects.get_or_create(
            email=request.query_params.get("email"),
            defaults={"username": request.query_params.get("email")},
        )

        serializer = self.get_serializer(user[0])
        return Response(serializer.data)
