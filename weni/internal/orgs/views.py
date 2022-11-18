from django.conf import settings
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework import exceptions
from rest_framework import status
from rest_framework.mixins import CreateModelMixin

from weni.internal.views import InternalGenericViewSet
from weni.internal.orgs.serializers import (
    TemplateOrgSerializer,
    OrgCreateSerializer,
    OrgSerializer,
    OrgUpdateSerializer,
)

from temba.orgs.models import Org


class TemplateOrgViewSet(CreateModelMixin, InternalGenericViewSet):
    serializer_class = TemplateOrgSerializer


class OrgViewSet(viewsets.ModelViewSet, InternalGenericViewSet):
    queryset = Org.objects
    lookup_field = "uuid"

    def list(self, request):
        user = self.get_user(request)
        orgs = self.get_orgs(user)

        serializer = OrgSerializer(orgs, many=True)

        return Response(serializer.data)

    def create(self, request):
        serializer = OrgCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user, created = User.objects.get_or_create(
            email=request.data.get("user_email"), defaults={"username": request.data.get("user_email")}
        )

        org = Org.objects.create(
            name=request.data.get("name"),
            timezone=request.data.get("timezone"),
            created_by=user,
            modified_by=user,
            plan="infinity",
        )

        org.administrators.add(user)
        org.initialize()

        org_serializer = OrgSerializer(org)

        return Response(org_serializer.data)

    def retrieve(self, request, uuid=None):
        org = get_object_or_404(Org, uuid=uuid)
        serializer = OrgSerializer(org)

        return Response(serializer.data)

    def destroy(self, request, uuid=None):
        org = get_object_or_404(Org, uuid=uuid)
        user = get_object_or_404(User, email=request.query_params.get("user_email"))

        self.pre_destroy(org, user)
        org.release(user)

        return Response(status=status.HTTP_204_NO_CONTENT)

    def partial_update(self, request, uuid=None):
        org = get_object_or_404(Org, uuid=uuid)

        serializer = OrgUpdateSerializer(org, data=request.data)
        serializer.is_valid(raise_exception=True)

        modified_by = serializer.validated_data.get("modified_by", None)
        plan = serializer.validated_data.get("plan", None)

        if modified_by and not self._user_has_permisson(modified_by, org) and not modified_by.is_superuser:
            raise exceptions.ValidationError(
                f"User: {modified_by.pk} has no permission to update Org: {org.uuid}",
            )

        if plan is not None and plan == settings.INFINITY_PLAN:
            org.uses_topups = False
            org.plan_end = None

            serializer.save(plan_end=None)
            return Response(serializer.data)

        serializer.save()
        return Response(serializer.data)

    def pre_destroy(self, org: Org, user: User):
        if user.id and user.id > 0 and hasattr(org, "modified_by_id"):
            org.modified_by = user

            # Interim fix, remove after implementation in the model.
            org.save(update_fields=["modified_by"])

    def get_user(self, request):
        user_email = request.query_params.get("user_email")

        if not user_email:
            raise exceptions.ValidationError("Email cannot be null")

        return get_object_or_404(User, email=request.query_params.get("user_email"))

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
