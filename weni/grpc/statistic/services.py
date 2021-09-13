from django_grpc_framework import generics

from weni.protobuf.flows.statistic_pb2 import OrgStatistic
from weni.grpc.core.services import AbstractService


class OrgStatisticService(generics.GenericService, AbstractService):
    def Retrieve(self, request, context):
        org = self.get_org_object(request.org_uuid, "uuid")

        response = {
            "active_flows": org.flows.filter(is_active=True, is_archived=False).exclude(is_system=True).count(),
            "active_classifiers": org.classifiers.filter(is_active=True).count(),
            "active_contacts": org.contacts.filter(is_active=True).count(),
        }

        return OrgStatistic(**response)
