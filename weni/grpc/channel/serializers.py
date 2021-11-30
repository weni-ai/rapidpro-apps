import json

from django_grpc_framework import proto_serializers
from rest_framework import serializers
from django.core.validators import URLValidator
from google.protobuf.empty_pb2 import Empty

from temba.channels.models import Channel
from temba.utils.fields import validate_external_url
from temba.channels.types.weniwebchat.type import CONFIG_BASE_URL
from weni.grpc.core import serializers as weni_serializers
from weni.protobuf.flows import channel_pb2


class WeniWebChatProtoSerializer(proto_serializers.ProtoSerializer):

    org = weni_serializers.OrgUUIDRelatedField(write_only=True)
    user = weni_serializers.UserEmailRelatedField(write_only=True)
    name = serializers.CharField()
    base_url = serializers.URLField(validators=[URLValidator(), validate_external_url], write_only=True)
    uuid = serializers.UUIDField(read_only=True)

    def create(self, validated_data):
        user = validated_data["user"]
        name = validated_data["name"]

        config = {CONFIG_BASE_URL: validated_data["base_url"]}

        return Channel.create(
            validated_data["org"],
            validated_data["user"],
            None,
            self._get_channel_type(),
            config=config,
            name=name,
            address=name,
        )

    def _get_channel_type(self):
        return self.context["service"].channel_type()

    class Meta:
        proto_class = channel_pb2.WeniWebChat
        fields = ["user", "name", "base_url", "uuid"]


class ChannelProtoSerializer(proto_serializers.ModelProtoSerializer):

    user = weni_serializers.UserEmailRelatedField(write_only=True, required=True)
    config = serializers.SerializerMethodField()

    def get_config(self, instance):
        return json.dumps(instance.config)

    class Meta:
        model = Channel
        proto_class = channel_pb2.Channel
        fields = ("user", "uuid", "name", "address", "config")
        read_only_fields = ("uuid", "name", "address", "config")
