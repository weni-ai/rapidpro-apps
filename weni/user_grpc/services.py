import grpc

from django.contrib.auth.models import User

from django_grpc_framework import generics, mixins

from weni.user_grpc.serializers import (
    UserPermissionProtoSerializer,
    UserProtoSerializer,
)

from temba.orgs.models import Org


class AbstractUserService(generics.GenericService):
    def get_org_object(self, pk: int) -> Org:
        return self._get_object(Org, pk)

    def get_user_object(self, pk: int) -> User:
        return self._get_object(User, pk)

    def _get_object(self, model, value: str, query_parameter: str = "pk"):

        query = {query_parameter: value}

        try:
            return model.objects.get(**query)
        except model.DoesNotExist:
            self.context.abort(grpc.StatusCode.NOT_FOUND, f"{model.__name__}: {value} not found!")


class UserPermissionService(AbstractUserService, mixins.RetrieveModelMixin, mixins.UpdateModelMixin):
    def Retrieve(self, request, context):
        org = self.get_org_object(request.org_id)
        user = self.get_user_object(request.user_id)

        permissions = self.get_user_permissions(org, user)

        serializer = UserPermissionProtoSerializer(permissions)

        return serializer.message

    def Update(self, request, context):
        org = self.get_org_object(request.org_id)
        user = self.get_user_object(request.user_id)

        self.validate_permission(org, request.permission)
        self.set_user_permission(org, user, request.permission)

        permissions = self.get_user_permissions(org, user)
        serializer = UserPermissionProtoSerializer(permissions)

        return serializer.message

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

        if org.administrators.filter(pk=user.id).exists():
            permissions["administrator"] = True

        if org.viewers.filter(pk=user.id).exists():
            permissions["viewer"] = True

        if org.editors.filter(pk=user.id).exists():
            permissions["editor"] = True

        if org.surveyors.filter(pk=user.id).exists():
            permissions["surveyor"] = True

        return permissions


class UserService(AbstractUserService, mixins.RetrieveModelMixin):

    serializer_class = UserProtoSerializer

    def get_user_object(self, email: str) -> User:
        return self._get_object(User, email, query_parameter="email")

    def get_object(self):
        return self.get_user_object(self.request.email)
