from django_grpc_framework import generics
from weni.billing.grpc_gen.billing_pb2 import BillingResponse
from weni.billing.queries import ActiveContactsQuery as Query
from weni.billing.serializers import BillingRequestSerializer as Serializer


class BillingService(generics.GenericService):
    def Total(self, request, context):
        serializer = Serializer(message=request)
        if serializer.is_valid():
            org_uuid = serializer.validated_data["org_uuid"]
            before = serializer.validated_data["before"]
            after = serializer.validated_data["after"]
            total_count = Query.total(org_uuid, before, after)
            return BillingResponse(active_contacts=total_count)
