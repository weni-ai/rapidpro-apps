from django_grpc_framework import generics

from temba.channels.types.weniwebchat.type import WeniWebChatType
from weni.grpc.channel.serializers import WeniWebChatProtoSerializer


class WeniWebChatService(generics.CreateService):

    channel_type = WeniWebChatType
    serializer_class = WeniWebChatProtoSerializer
