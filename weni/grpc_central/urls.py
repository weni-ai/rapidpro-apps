from weni.org_grpc.urls import grpc_handlers as org_handlers
from weni.flow_grpc.urls import grpc_handlers as flow_handlers
from weni.billing.urls import grpc_handlers as billing_handlers

def grpc_handlers(server):
    org_handlers(server)
    flow_handlers(server)
    billing_handlers(server)
