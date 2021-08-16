from django_grpc_framework import proto_serializers
from rest_framework import serializers
from django.core.validators import URLValidator

from temba.channels.models import Channel
from temba.utils.fields import validate_external_url
from temba.channels.types.weniwebchat.type import CONFIG_BASE_URL
from weni.grpc.core import serializers as weni_serializers
from weni.grpc.channel.grpc_gen import channel_pb2


class WeniWebChatProtoSerializer(proto_serializers.ProtoSerializer):

    user = weni_serializers.UserEmailRelatedField(write_only=True)
    name = serializers.CharField()
    base_url = serializers.URLField(validators=[URLValidator(), validate_external_url], write_only=True)

    def create(self, validated_data):
        user = validated_data["user"]
        name = validated_data["name"]

        config = {CONFIG_BASE_URL: validated_data["base_url"]}

        return Channel.create(
            user.get_org(), user, None, self._get_channel_type(), config=config, name=name, address=name
        )

    def _get_channel_type(self):
        return self.context["service"].channel_type()

    class Meta:
        proto_class = channel_pb2.WeniWebChat
        fields = ["user", "name", "base_url"]
