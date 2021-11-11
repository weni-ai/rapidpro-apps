import json
import re

from django.http import Http404, HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.auth.models import User
from django_grpc_framework import generics, mixins
from django.test import RequestFactory

from temba.channels.types.weniwebchat.type import WeniWebChatType
from temba.channels.models import Channel
from temba.orgs.models import Org
from temba.channels.types import TYPES

from weni.grpc.channel.serializers import WeniWebChatProtoSerializer, ChannelProtoSerializer
from weni.protobuf.flows import channel_pb2


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

    def Create(self, request, context):
        data: dict = None

        try:
            data = json.loads(request.data)
        except json.decoder.JSONDecodeError:
            raise HttpResponseBadRequest("Can't decode the `data` field")

        user = get_object_or_404(User, email=request.user)
        org = get_object_or_404(Org, uuid=request.org)

        channel_type = TYPES.get(request.channeltype_code, None)

        if channel_type is None:
            raise Http404(f"No channels found with '{request.channeltype_code}' code")

        url = self.create_channel(user, org, data, channel_type)
        regex = "[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12}"
        channe_uuid = re.findall(regex, url)[0]

        return channel_pb2.Channel(uuid=channe_uuid)

    def create_channel(self, user: User, org: Org, data: dict, channel_type) -> str:
        factory = RequestFactory()
        url = f"channels/types/{channel_type.slug}/claim"

        request = factory.post(url, data)
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()

        user._org = org
        request.user = user
        response = MessageMiddleware(channel_type.claim_view.as_view(channel_type=channel_type))(request)
        return response.url
