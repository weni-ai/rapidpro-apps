from weni.statistic_grpc.grpc_gen import statistic_pb2_grpc
from weni.statistic_grpc.services import OrgStatisticService


def grpc_handlers(server):
    statistic_pb2_grpc.add_OrgStatisticControllerServicer_to_server(OrgStatisticService.as_servicer(), server)
