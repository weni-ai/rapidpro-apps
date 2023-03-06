from django.shortcuts import get_object_or_404

from rest_framework.response import Response
from rest_framework.mixins import RetrieveModelMixin
from rest_framework import status

from temba.orgs.models import Org
from weni.internal.models import Project

from weni.internal.views import InternalGenericViewSet


class StatisticEndpoint(RetrieveModelMixin, InternalGenericViewSet):
    lookup_field = "project_uuid"

    def retrieve(self, request, project_uuid=None):
        project = get_object_or_404(Project, project_uuid=project_uuid)

        response = {
            "active_flows": project.flows.filter(is_active=True, is_archived=False).exclude(is_system=True).count(),
            "active_classifiers": project.classifiers.filter(is_active=True).count(),
            "active_contacts": project.contacts.filter(is_active=True).count(),
        }

        return Response(data=response, status=status.HTTP_200_OK)
