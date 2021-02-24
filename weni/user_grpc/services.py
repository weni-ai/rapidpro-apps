import grpc

from django.contrib.auth.models import User

from django_grpc_framework import generics, mixins

from weni.user_grpc.serializers import UserPermissionProtoSerializer

from temba.orgs.models import Org


class AbstractUserService(generics.GenericService):
    def get_org_object(self, pk: int) -> Org:
        return self._get_object(Org, pk)

    def get_user_object(self, pk: int) -> User:
        return self._get_object(User, pk)

    def _get_object(self, model, pk: int):

        try:
            return model.objects.get(pk=pk)
        except model.DoesNotExist:
            self.validate_pk(model, pk)
            self.context.abort(grpc.StatusCode.NOT_FOUND, f"{model.__name__}: {pk} not found!")

    def validate_pk(self, model, pk: int):
        if not pk:
            self.context.abort(grpc.StatusCode.NOT_FOUND, f"{model.__name__} pk cannot be 0 or None")


class UserPermissionService(AbstractUserService, mixins.ListModelMixin):
    def Retrieve(self, request, context):
        org = self.get_org_object(request.org_id)
        self.validate_pk(User, request.user_id)

        permissions = {}

        if org.administrators.filter(pk=request.user_id).exists():
            permissions["administrator"] = True

        if org.viewers.filter(pk=request.user_id).exists():
            permissions["viewer"] = True

        if org.editors.filter(pk=request.user_id).exists():
            permissions["editor"] = True

        if org.surveyors.filter(pk=request.user_id).exists():
            permissions["surveyor"] = True

        serializer = UserPermissionProtoSerializer(permissions)

        return serializer.message
