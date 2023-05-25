import json

from django_grpc_framework import proto_serializers
from rest_framework import serializers
from django.core.validators import URLValidator

from temba.channels.models import Channel
from temba.utils.fields import validate_external_url
from temba.channels.types.weniwebchat.type import CONFIG_BASE_URL
from temba.utils import analytics
from weni.grpc.core import serializers as weni_serializers
from weni.protobuf.flows import channel_pb2
from weni.grpc.channel import fields


class WeniWebChatProtoSerializer(proto_serializers.ProtoSerializer):
    org = weni_serializers.OrgUUIDRelatedField(write_only=True)
    user = weni_serializers.UserEmailRelatedField(write_only=True)
    name = serializers.CharField()
    base_url = serializers.URLField(validators=[URLValidator(), validate_external_url], write_only=True)
    uuid = serializers.UUIDField(read_only=True)

    def create(self, validated_data):
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
    org = serializers.SerializerMethodField()

    def get_config(self, instance):
        return json.dumps(instance.config)

    def get_org(self, instance):
        return str(instance.org.uuid)

    class Meta:
        model = Channel
        proto_class = channel_pb2.Channel
        fields = ("user", "uuid", "name", "address", "config", "org", "is_active")
        read_only_fields = ("uuid", "name", "address", "config", "org", "is_active")


class ChannelWACSerializer(proto_serializers.ModelProtoSerializer):
    user = weni_serializers.UserEmailRelatedField(required=True, write_only=True)
    org = weni_serializers.OrgUUIDRelatedField(required=True, write_only=True)
    phone_number_id = serializers.CharField(required=True, write_only=True)
    uuid = serializers.CharField(read_only=True)
    name = serializers.CharField(read_only=True)
    address = serializers.CharField(read_only=True)
    config = fields.ConfigCharField(required=True)

    class Meta:
        model = Channel
        proto_class = channel_pb2.Channel
        fields = ("user", "org", "phone_number_id", "uuid", "name", "address", "config")

    def validate_phone_number_id(self, value):
        if Channel.objects.filter(is_active=True, address=value).exists():
            raise serializers.ValidationError("a Channel with that 'phone_number_id' alredy exists")
        return value

    def get_config(self, instance):
        return json.dumps(instance)

    def create(self, validated_data):
        channel_type = Channel.get_type_from_code("WAC")
        schemes = channel_type.schemes

        org = validated_data.get("org")
        phone_number_id = validated_data.get("phone_number_id")
        config = validated_data.get("config", {})
        user = validated_data.get("user")

        number = config.get("wa_number")
        verified_name = config.get("wa_verified_name")
        name = f"{number} - {verified_name}"

        channel = Channel.objects.create(
            org=org,
            country=None,
            channel_type=channel_type.code,
            name=name,
            address=phone_number_id,
            config=config,
            role=Channel.DEFAULT_ROLE,
            schemes=schemes,
            created_by=user,
            modified_by=user,
        )

        analytics.track(user, "temba.channel_created", dict(channel_type=channel_type.code))

        return channel
