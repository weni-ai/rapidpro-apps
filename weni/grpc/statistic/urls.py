from weni.protobuf.flows import statistic_pb2_grpc
from weni.grpc.statistic.services import OrgStatisticService


def grpc_handlers(server):
    statistic_pb2_grpc.add_OrgStatisticControllerServicer_to_server(OrgStatisticService.as_servicer(), server)
