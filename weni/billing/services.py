from django_grpc_framework import generics
from weni.billing.grpc_gen.billing_pb2 import BillingResponse
from weni.billing.queries import ActiveContactsQuery as Query

class BillingService(generics.GenericService):
    def Total(self, request, context):
        return BillingResponse(active_contacts=Query.total(request.org_uuid, request.before, request.after))
