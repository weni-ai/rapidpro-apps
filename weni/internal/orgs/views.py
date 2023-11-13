from django.conf import settings
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

from rest_framework.decorators import action
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
    UpdateProjectSerializer,
)

from weni.internal.models import Project


class TemplateOrgViewSet(CreateModelMixin, InternalGenericViewSet):
    serializer_class = TemplateOrgSerializer


class OrgViewSet(viewsets.ModelViewSet, InternalGenericViewSet):
    queryset = Project.objects
    lookup_field = "project_uuid"

    def list(self, request):
        user = self.get_user(request)
        orgs_ids = self.get_orgs(user).values_list("id", flat=True)
        projects = Project.objects.filter(id__in=orgs_ids)
        serializer = OrgSerializer(projects, many=True)

        return Response(serializer.data)

    def create(self, request):
        serializer = OrgCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user, created = User.objects.get_or_create(
            email=request.data.get("user_email"),
            defaults={"username": request.data.get("user_email")},
        )

        project = Project.objects.create(
            name=request.data.get("name"),
            timezone=request.data.get("timezone"),
            created_by=user,
            modified_by=user,
            plan="infinity",
            project_uuid=request.data.get("uuid"),
        )

        project.administrators.add(user)
        project.initialize()

        org_serializer = OrgSerializer(project)

        return Response(org_serializer.data)

    def retrieve(self, request, project_uuid=None):
        project = get_object_or_404(Project, project_uuid=project_uuid)
        serializer = OrgSerializer(project)

        return Response(serializer.data)

    def destroy(self, request, project_uuid=None):
        project = get_object_or_404(Project, project_uuid=project_uuid)
        user = get_object_or_404(User, email=request.query_params.get("user_email"))

        self.pre_destroy(project, user)
        project.release(user)

        return Response(status=status.HTTP_204_NO_CONTENT)

    def partial_update(self, request, project_uuid=None):
        project = get_object_or_404(Project, project_uuid=project_uuid)

        serializer = OrgUpdateSerializer(project, data=request.data)
        serializer.is_valid(raise_exception=True)

        modified_by = serializer.validated_data.get("modified_by", None)
        plan = serializer.validated_data.get("plan", None)

        if (
            modified_by
            and not self._user_has_permisson(modified_by, project)
            and not modified_by.is_superuser
        ):
            raise exceptions.ValidationError(
                f"User: {modified_by.pk} has no permission to update Org: {project.project_uuid}",
            )

        if plan is not None and plan == settings.INFINITY_PLAN:
            project.uses_topups = False
            project.plan_end = None

            serializer.save(plan_end=None)
            return Response(serializer.data)

        serializer.save()
        return Response(serializer.data)

    def pre_destroy(self, org: Project, user: User):
        if user.id and user.id > 0 and hasattr(org, "modified_by_id"):
            org.modified_by = user

            # Interim fix, remove after implementation in the model.
            org.save(update_fields=["modified_by"])

    def get_user(self, request):
        user_email = request.query_params.get("user_email")

        if not user_email:
            raise exceptions.ValidationError("Email cannot be null")

        return get_object_or_404(User, email=request.query_params.get("user_email"))

    def _user_has_permisson(self, user: User, project: Project) -> bool:
        return (
            user.org_admins.filter(pk=project.pk)
            or user.org_viewers.filter(pk=project.pk)
            or user.org_editors.filter(pk=project.pk)
            or user.org_surveyors.filter(pk=project.pk)
        )

    def get_orgs(self, user: User):
        admins = user.org_admins.filter(is_active=True)
        viewers = user.org_viewers.filter(is_active=True)
        editors = user.org_editors.filter(is_active=True)
        surveyors = user.org_surveyors.filter(is_active=True)

        return admins.union(viewers, editors, surveyors)

    @action(methods=["POST", "DELETE"], detail=True, url_path="update-vtex")
    def update_vtex(self, request, project_uuid=None):
        project = self.get_object()
        serializer = UpdateProjectSerializer(project, data=request.data)
        serializer.is_valid(raise_exception=True)
        modified_by = serializer.validated_data.get("modified_by", None)

        if (
            modified_by
            and not self._user_has_permisson(modified_by, project)
            and not modified_by.is_superuser
        ):
            raise exceptions.ValidationError(
                f"User: {modified_by.pk} has no permission to update Org: {project.project_uuid}",
            )

        if request.method == "POST":
            project.config["has_vtex"] = True
            project.save(update_fields=["config"])
            return Response(status=status.HTTP_200_OK, data=serializer.data)

        elif request.method == "DELETE":
            if "has_vtex" in project.config:
                del project.config["has_vtex"]
                project.save(update_fields=["config"])
            return Response(status=status.HTTP_204_NO_CONTENT)
