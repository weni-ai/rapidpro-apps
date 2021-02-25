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


class UserPermissionService(AbstractUserService, mixins.RetrieveModelMixin):
    def Retrieve(self, request, context):
        org = self.get_org_object(request.org_id)
        user = self.get_user_object(request.user_id)

        permissions = {}

        if org.administrators.filter(pk=user.id).exists():
            permissions["administrator"] = True

        if org.viewers.filter(pk=user.id).exists():
            permissions["viewer"] = True

        if org.editors.filter(pk=user.id).exists():
            permissions["editor"] = True

        if org.surveyors.filter(pk=user.id).exists():
            permissions["surveyor"] = True

        serializer = UserPermissionProtoSerializer(permissions)

        return serializer.message


class UserService(AbstractUserService, mixins.RetrieveModelMixin):

    serializer_class = UserProtoSerializer

    def get_user_object(self, email: str) -> User:
        return self._get_object(User, email, query_parameter="email")

    def get_object(self):
        return self.get_user_object(self.request.email)
