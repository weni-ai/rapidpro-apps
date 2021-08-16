from weni.grpc.channel.grpc_gen import channel_pb2_grpc
from weni.grpc.channel import services


def grpc_handlers(server):
    channel_pb2_grpc.add_WeniWebChatControllerServicer_to_server(services.WeniWebChatService.as_servicer(), server)
