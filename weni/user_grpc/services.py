from django.conf import settings
from django.contrib.auth.models import User

import grpc

from django_grpc_framework import generics, mixins

from weni.user_grpc.serializers import (
    UserPermissionProtoSerializer,
    UserProtoSerializer,
)
from weni.grpc_central.services import AbstractService

from temba.orgs.models import Org


class UserPermissionService(
    AbstractService, generics.GenericService, mixins.RetrieveModelMixin, mixins.UpdateModelMixin
):
    def Retrieve(self, request, context):
        org = self.get_org_object(request.org_uuid, "uuid")
        user = self.get_user_object(request.user_email, "email")

        permissions = self.get_user_permissions(org, user)

        serializer = UserPermissionProtoSerializer(permissions)

        return serializer.message

    def Update(self, request, context):
        org = self.get_org_object(request.org_uuid, "uuid")
        user = self.get_user_object(request.user_email, "email")

        self.validate_permission(org, request.permission)
        self.set_user_permission(org, user, request.permission)

        permissions = self.get_user_permissions(org, user)
        serializer = UserPermissionProtoSerializer(permissions)

        return serializer.message

    def Remove(self, request, context):
        org = self.get_org_object(request.org_uuid, "uuid")
        user = self.get_user_object(request.user_email, "email")

        self.validate_permission(org, request.permission)
        self.remove_user_permission(org, user, request.permission)

        permissions = self.get_user_permissions(org, user)
        serializer = UserPermissionProtoSerializer(permissions)

        return serializer.message

    def remove_user_permission(self, org: Org, user: User, permission: str):
        permissions = self.get_permissions(org)
        permissions.get(permission).remove(user)

    def set_user_permission(self, org: Org, user: User, permission: str):
        permissions = self.get_permissions(org)

        for perm_name, org_field in permissions.items():
            if not perm_name == permission:
                org_field.remove(user)

        permissions.get(permission).add(user)

    def validate_permission(self, org: Org, permission: str):
        permissions_keys = self.get_permissions(org).keys()

        if permission not in permissions_keys:
            self.context.abort(grpc.StatusCode.NOT_FOUND, f"{permission} is not a valid permission!")

    def get_permissions(self, org: Org) -> dict:
        return {
            "administrator": org.administrators,
            "viewer": org.viewers,
            "editor": org.editors,
            "surveyor": org.surveyors,
        }

    def get_user_permissions(self, org: Org, user: User) -> dict:
        permissions = {}
        org_permissions = self.get_permissions(org)

        for perm_name, org_field in org_permissions.items():
            if org_field.filter(pk=user.id).exists():
                permissions[perm_name] = True

        return permissions


class UserService(generics.GenericService, AbstractService, mixins.RetrieveModelMixin):

    serializer_class = UserProtoSerializer

    def Update(self, request, context):

        if request.language not in [language[0] for language in settings.LANGUAGES]:
            self.context.abort(grpc.StatusCode.INVALID_ARGUMENT, f"Invalid argument: language")

        user = self.get_object()
        user_settings = user.get_settings()
        user_settings.language = request.language
        user_settings.save()

        serializer = UserProtoSerializer(user)

        return serializer.message

    def get_object(self):
        return self.get_user_object(self.request.email, "email")