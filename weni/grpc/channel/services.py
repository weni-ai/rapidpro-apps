from django_grpc_framework import generics, mixins

from temba.channels.types.weniwebchat.type import WeniWebChatType
from temba.channels.models import Channel
from weni.grpc.channel.serializers import WeniWebChatProtoSerializer, ChannelProtoSerializer


# this class will be deprecated
class WeniWebChatService(mixins.CreateModelMixin, mixins.DestroyModelMixin, generics.GenericService):

    channel_type = WeniWebChatType
    serializer_class = WeniWebChatProtoSerializer


class ChannelService(generics.DestroyService):

    queryset = Channel.objects
    lookup_field = "uuid"
    serializer_class = ChannelProtoSerializer

    def perform_destroy(self, instance):
        serializer = self.get_serializer(message=self.request)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data.get("user")
        instance.release(user)
