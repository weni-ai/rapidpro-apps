import grpc
from django.utils import timezone as tz
from django_grpc_framework.proto_serializers import ProtoSerializer
from rest_framework import serializers

from temba.api.v2.fields import TranslatableField
from weni.protobuf.flows import billing_pb2
from weni.grpc.core import serializers as weni_serializers


class BillingRequestSerializer(ProtoSerializer):
    org = weni_serializers.OrgUUIDRelatedField(write_only=True)
    before = serializers.DateTimeField()
    after = serializers.DateTimeField()

    def validate(self, data):
        if data["after"] > data["before"]:
            self.context.get("grpc_context").abort(
                grpc.StatusCode.INVALID_ARGUMENT, '"after" should be earlier then "before"'
            )
        return data

    def validate_after(self, value):
        if value > tz.now():
            self.context.get("grpc_context").abort(grpc.StatusCode.INVALID_ARGUMENT, "Cannot search after this date.")
        return value

    class Meta:
        proto_class = billing_pb2.BillingRequest


class MsgSerializer(ProtoSerializer):
    uuid = serializers.UUIDField()
    text = TranslatableField()
    sent_on = serializers.DateTimeField()
    direction = serializers.CharField()

    class Meta:
        proto_class = billing_pb2.Msg


class ChannelSerializer(ProtoSerializer):
    uuid = serializers.UUIDField()
    channel_id = serializers.IntegerField()
    name = serializers.CharField()

    class Meta:
        proto_class = billing_pb2.Channel


class ActiveContactDetailSerializer(ProtoSerializer):
    uuid = serializers.UUIDField()
    name = serializers.CharField()
    msg = MsgSerializer()
    channel = ChannelSerializer()

    def to_representation(self, flat_data):
        direction_map = {"I": billing_pb2.INPUT, "O": billing_pb2.OUTPUT}
        instance = {
            "uuid": flat_data["uuid"],
            "name": flat_data["name"],
            "msg": {
                "uuid": flat_data["msg__uuid"],
                "text": flat_data["msg__text"],
                "sent_on": flat_data["msg__sent_on"],
                "direction": direction_map[flat_data["msg__direction"]],
            },
            "channel": {
                "uuid": flat_data["channel__uuid"],
                "channel_id": flat_data["channel__id"],
                "name": flat_data["channel__name"],
            },
        }
        return super().to_representation(instance)

    def message_to_data(self, data):
        return NotImplemented

    class Meta:
        proto_class = billing_pb2.ActiveContactDetail


class MessageDetailRequestSerializer(ProtoSerializer):
    org_uuid = serializers.UUIDField()
    contact_uuid = serializers.CharField()
    before = serializers.DateTimeField()
    after = serializers.DateTimeField()

    class Meta:
        proto_class = billing_pb2.MessageDetailRequest


class MsgDetailSerializer(ProtoSerializer):
    uuid = serializers.UUIDField()
    text = serializers.CharField()
    created_on = serializers.CharField()
    direction = serializers.CharField()
    channel_id = serializers.IntegerField()
    channel_type = serializers.CharField()

    class Meta:
        proto_class = billing_pb2.MsgDetail
