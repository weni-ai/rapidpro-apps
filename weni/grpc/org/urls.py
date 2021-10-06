from weni.protobuf.flows import org_pb2_grpc
from weni.grpc.org.services import OrgService


def grpc_handlers(server):
    org_pb2_grpc.add_OrgControllerServicer_to_server(OrgService.as_servicer(), server)
