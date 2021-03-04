from django_grpc_framework import generics

from weni.statistic_grpc.grpc_gen.statistic_pb2 import OrgStatistic
from weni.grpc_central.services import AbstractService


class OrgStatisticService(generics.GenericService, AbstractService):
    def Retrieve(self, request, context):
        org = self.get_org_object(request.org_uuid, "uuid")

        response = {
            "active_flows": org.flows.filter(is_active=True).count(),
            "active_classifier": org.classifiers.filter(is_active=True).count(),
            "active_contacts": org.contacts.filter(is_active=True).count(),
        }

        return OrgStatistic(**response)
