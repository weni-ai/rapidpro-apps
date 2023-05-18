from django.shortcuts import get_object_or_404

from rest_framework.response import Response
from rest_framework.mixins import RetrieveModelMixin
from rest_framework import status

from temba.orgs.models import Org
from temba.contacts.models import ContactGroup

from weni.internal.views import InternalGenericViewSet


class StatisticEndpoint(RetrieveModelMixin, InternalGenericViewSet):
    lookup_field = "uuid"

    def retrieve(self, request, uuid=None):
        org = get_object_or_404(Org, uuid=uuid, is_active=True)
        group = ContactGroup.all_groups.get(org=org, group_type='A')

        response = {
            "active_flows": org.flows.filter(is_active=True, is_archived=False).exclude(is_system=True).count(),
            "active_classifiers": org.classifiers.filter(is_active=True).count(),
            "active_contacts": group.get_member_count(),
        }

        return Response(data=response, status=status.HTTP_200_OK)
