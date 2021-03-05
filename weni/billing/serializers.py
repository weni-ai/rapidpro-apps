from datetime import datetime

from django.utils import timezone as tz
from django_grpc_framework.proto_serializers import (ProtoSerializer,
                                                     ValidationError)
from google.protobuf.timestamp_pb2 import Timestamp
from rest_framework import serializers

from weni.billing.grpc_gen import billing_pb2


class TimestampField(serializers.Field):
    def to_representation(self, value: datetime) -> Timestamp:
        if tz.is_naive(value):
            raise ValidationError("You should consider use timezone-aware datetime objects.")
        ts = value.timestamp()
        seconds = int(ts)
        nanos = int((ts - seconds) * 10 ** 9)
        return Timestamp(seconds=seconds, nanos=nanos)

    def to_internal_value(self, message: Timestamp) -> datetime:
        ts = message.seconds + message.nanos / 10 ** 9
        return datetime.fromtimestamp(ts, tz=tz.utc)


class BillingRequestSerializer(ProtoSerializer):
    org_uuid = serializers.UUIDField()
    before = TimestampField()
    after = TimestampField()

    class Meta:
        proto_class = billing_pb2.BillingRequest
