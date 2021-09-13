from weni.protobuf.flows import flow_pb2_grpc
from weni.grpc.flow.services import FlowService


def grpc_handlers(server):
    flow_pb2_grpc.add_FlowControllerServicer_to_server(FlowService.as_servicer(), server)
