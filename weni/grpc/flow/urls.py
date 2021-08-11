from weni.flow_grpc.grpc_gen import flow_pb2_grpc
from weni.flow_grpc.services import FlowService


def grpc_handlers(server):
    flow_pb2_grpc.add_FlowControllerServicer_to_server(FlowService.as_servicer(), server)
