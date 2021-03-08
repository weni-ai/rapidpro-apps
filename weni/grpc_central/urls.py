from weni.org_grpc.urls import grpc_handlers as org_handlers
from weni.flow_grpc.urls import grpc_handlers as flow_handlers
from weni.statistic_grpc.urls import grpc_handlers as statistic_handlers
from weni.user_grpc.urls import grpc_handlers as user_handlers


def grpc_handlers(server):
    org_handlers(server)
    flow_handlers(server)
    statistic_handlers(server)
    user_handlers(server)
