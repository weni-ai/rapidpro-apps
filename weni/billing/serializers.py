from django_grpc_framework.proto_serializers import ProtoSerializer
from rest_framework import serializers

from weni.billing.grpc_gen import billing_pb2


class BillingRequestSerializer(ProtoSerializer):
    org_uuid = serializers.UUIDField()
    before = serializers.DateTimeField()
    after = serializers.DateTimeField()

    class Meta:
        proto_class = billing_pb2.BillingRequest
