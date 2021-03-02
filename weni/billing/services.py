from django_grpc_framework import generics
from weni.billing.grpc_gen.billing_pb2 import BillingResponse

class BillingService(generics.GenericService):
    def Total(self, request, context):
        return BillingResponse(active_contacts=42)
