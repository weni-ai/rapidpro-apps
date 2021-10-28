from weni.protobuf.flows import channel_pb2_grpc
from weni.grpc.channel import services


def grpc_handlers(server):
    channel_pb2_grpc.add_ChannelControllerServicer_to_server(services.ChannelService.as_servicer(), server)
    channel_pb2_grpc.add_WeniWebChatControllerServicer_to_server(services.WeniWebChatService.as_servicer(), server)
