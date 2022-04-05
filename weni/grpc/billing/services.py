from django_grpc_framework import generics

from weni.protobuf.flows.billing_pb2 import TotalResponse
from weni.grpc.billing.queries import ActiveContactsQuery as Query
from weni.grpc.billing.serializers import BillingRequestSerializer, ActiveContactDetailSerializer


class BillingService(generics.GenericService):

    serializer_class = BillingRequestSerializer

    def Total(self, request, context):
        serializer = self.get_serializer(message=request)
        serializer.is_valid(raise_exception=True)

        org = serializer.validated_data["org"]
        before = serializer.validated_data["before"]
        after = serializer.validated_data["after"]
        total_count = Query.total(str(org.uuid), before, after)

        return TotalResponse(active_contacts=total_count)

    def Detailed(self, request, context):
        serializer = self.get_serializer(message=request)
        serializer.is_valid(raise_exception=True)

        org = serializer.validated_data["org"]
        before = serializer.validated_data["before"]
        after = serializer.validated_data["after"]
        results = Query.detailed(str(org.uuid), before, after)

        for message in ActiveContactDetailSerializer(results, many=True).message:
            yield message
