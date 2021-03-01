import grpc
from django.contrib.auth.models import User
from django_grpc_framework import generics, mixins
from google.protobuf import empty_pb2

from temba.orgs.models import Org
from weni.org_grpc.serializers import OrgCreateProtoSerializer, OrgProtoSerializer, OrgUpdateProtoSerializer


class OrgService(generics.GenericService, mixins.ListModelMixin):
    def List(self, request, context):

        user = self.get_user(request)
        orgs = self.get_orgs(user)

        serializer = OrgProtoSerializer(orgs, many=True)

        for msg in serializer.message:
            yield msg

    def Create(self, request, context):
        serializer = OrgCreateProtoSerializer(message=request)
        serializer.is_valid(raise_exception=True)

        user = User.objects.get(id=serializer.validated_data.get("user_id"))
        validated_data = {
            "name": serializer.validated_data.get("name"),
            "timezone": serializer.validated_data.get("timezone"),
            "created_by": user,
            "modified_by": user,
        }

        org = Org.objects.create(**validated_data)

        org_serializer = OrgProtoSerializer(org)

        return org_serializer.message

    def Destroy(self, request, context):
        org = self.get_org_object(request.id)
        user = self.get_user_object(request.user_id)

        self.pre_destroy(org, user)
        org.release()

        return empty_pb2.Empty()

    def Update(self, request, context):
        serializer = OrgUpdateProtoSerializer(message=request)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return serializer.message

    def pre_destroy(self, org: Org, user: User):
        if user.id and user.id > 0 and hasattr(org, "modified_by_id"):
            org.modified_by = user

            # Interim fix, remove after implementation in the model.
            org.save(update_fields=["modified_by"])

    def get_org_object(self, pk: int) -> Org:
        return self._get_object(Org, pk)

    def get_user_object(self, pk: int) -> User:
        return self._get_object(User, pk)

    def _get_object(self, model, pk: int):
        try:
            return model.objects.get(pk=pk)
        except model.DoesNotExist:
            self.context.abort(grpc.StatusCode.NOT_FOUND, f"{model.__name__}: {pk} not found!")

    def get_user(self, request):
        user_email = request.user_email

        if not user_email:
            self.context.abort(grpc.StatusCode.NOT_FOUND, "Email cannot be null")

        try:
            return User.objects.get(email=request.user_email)
        except User.DoesNotExist:
            self.context.abort(grpc.StatusCode.NOT_FOUND, f"User:{request.user_email} not found!")

    def get_orgs(self, user: User):
        return user.org_admins.union(user.org_viewers.all(), user.org_editors.all(), user.org_surveyors.all())
