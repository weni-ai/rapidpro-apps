from weni.protobuf.flows import billing_pb2_grpc
from weni.grpc.billing.services import BillingService


def grpc_handlers(server):
    billing_pb2_grpc.add_BillingControllerServicer_to_server(BillingService.as_servicer(), server)
