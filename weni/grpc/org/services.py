import grpc
from django.contrib.auth.models import User
from django.conf import settings
from django_grpc_framework import generics, mixins
from google.protobuf import empty_pb2

from temba.orgs.models import Org
from weni.grpc.org.serializers import (
    OrgCreateProtoSerializer,
    OrgProtoSerializer,
    OrgUpdateProtoSerializer,
)
from weni.grpc.core.services import AbstractService


class OrgService(AbstractService, generics.GenericService, mixins.ListModelMixin):
    queryset = Org.objects
    lookup_field = "uuid"

    def List(self, request, context):
        user = self.get_user(request)
        orgs = self.get_orgs(user)

        serializer = OrgProtoSerializer(orgs, many=True)

        for msg in serializer.message:
            yield msg

    def Create(self, request, context):
        serializer = OrgCreateProtoSerializer(message=request)
        serializer.is_valid(raise_exception=True)

        user, created = User.objects.get_or_create(email=request.user_email, defaults={"username": request.user_email})

        org = Org.objects.create(
            name=request.name,
            timezone=request.timezone,
            created_by=user,
            modified_by=user,
            plan="infinity",
        )

        org.administrators.add(user)
        org.initialize()

        org_serializer = OrgProtoSerializer(org)

        return org_serializer.message

    def Retrieve(self, request, context):
        org = self.get_org_object(request.uuid, "uuid")
        serializer = OrgProtoSerializer(org)

        return serializer.message

    def Destroy(self, request, context):
        org = self.get_org_object(request.uuid, "uuid")
        user = self.get_user_object(request.user_email, "email")

        self.pre_destroy(org, user)
        org.release(user)

        return empty_pb2.Empty()

    def Update(self, request, context):
        org = self.get_object()

        serializer = OrgUpdateProtoSerializer(org, message=request)
        serializer.is_valid(raise_exception=True)

        data = dict(serializer.validated_data)
        modified_by = data.get("modified_by", None)
        plan = data.get("plan", None)

        if modified_by and not self._user_has_permisson(modified_by, org) and not modified_by.is_superuser:
            self.context.abort(
                grpc.StatusCode.PERMISSION_DENIED,
                f"User: {modified_by.pk} has no permission to update Org: {org.uuid}",
            )

        if plan is not None and plan == settings.INFINITY_PLAN:
            org.uses_topups = False
            org.plan_end = None

            serializer.save(plan_end=None)
            return serializer.message

        serializer.save()
        return serializer.message

    def pre_destroy(self, org: Org, user: User):
        if user.id and user.id > 0 and hasattr(org, "modified_by_id"):
            org.modified_by = user

            # Interim fix, remove after implementation in the model.
            org.save(update_fields=["modified_by"])

    def get_user(self, request):
        user_email = request.user_email

        if not user_email:
            self.context.abort(grpc.StatusCode.NOT_FOUND, "Email cannot be null")

        try:
            return User.objects.get(email=request.user_email)
        except User.DoesNotExist:
            self.context.abort(grpc.StatusCode.NOT_FOUND, f"User:{request.user_email} not found!")

    def _user_has_permisson(self, user: User, org: Org) -> bool:
        return (
            user.org_admins.filter(pk=org.pk)
            or user.org_viewers.filter(pk=org.pk)
            or user.org_editors.filter(pk=org.pk)
            or user.org_surveyors.filter(pk=org.pk)
        )

    def get_orgs(self, user: User):
        admins = user.org_admins.filter(is_active=True)
        viewers = user.org_viewers.filter(is_active=True)
        editors = user.org_editors.filter(is_active=True)
        surveyors = user.org_surveyors.filter(is_active=True)

        return admins.union(viewers, editors, surveyors)
