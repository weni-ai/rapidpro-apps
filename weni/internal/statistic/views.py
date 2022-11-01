from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.mixins import RetrieveModelMixin
from rest_framework import status

from temba.orgs.models import Org

from weni.internal.views import InternalGenericViewSet


class StatisticEndpoint(RetrieveModelMixin, InternalGenericViewSet):
    lookup_field = "uuid"

    def retrieve(self, request, *args, **kwargs):
        params = self.request.query_params

        org_uuid = params.get("uuid", None)

        if not org_uuid:
            return Response({"error": "uuid is requored"}, status=status.HTTP_400_BAD_REQUEST)

        org = Org.objects.get(uuid=org_uuid)

        response = {
            "active_flows": org.flows.filter(is_active=True, is_archived=False).exclude(is_system=True).count(),
            "active_classifiers": org.classifiers.filter(is_active=True).count(),
            "active_contacts": org.contacts.filter(is_active=True).count(),
        }

        return JsonResponse(data=response, status=status.HTTP_200_OK)
