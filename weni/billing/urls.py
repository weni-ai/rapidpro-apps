from weni.billing.grpc_gen import billing_pb2_grpc
from weni.billing.services import BillingService


def grpc_handlers(server):
    billing_pb2_grpc.add_BillingServicer_to_server(BillingService.as_servicer(), server)
