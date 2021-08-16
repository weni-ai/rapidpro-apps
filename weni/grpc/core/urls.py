from weni.grpc.billing.urls import grpc_handlers as billing_handlers
from weni.grpc.flow.urls import grpc_handlers as flow_handlers
from weni.grpc.org.urls import grpc_handlers as org_handlers
from weni.grpc.statistic.urls import grpc_handlers as statistic_handlers
from weni.grpc.user.urls import grpc_handlers as user_handlers
from weni.grpc.classifier.urls import grpc_handlers as classifier_handlers
from weni.grpc.channel.urls import grpc_handlers as channel_handlers


def grpc_handlers(server):
    org_handlers(server)
    flow_handlers(server)
    billing_handlers(server)
    statistic_handlers(server)
    user_handlers(server)
    classifier_handlers(server)
    channel_handlers(server)
