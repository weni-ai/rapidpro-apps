from weni.protobuf.flows import flow_pb2

from django_grpc_framework import proto_serializers

from temba.flows.models import Flow
from temba.triggers.models import Trigger


class FlowTriggerProtoSerializer(proto_serializers.ModelProtoSerializer):
    class Meta:
        model = Trigger
        proto_class = flow_pb2.Trigger
        fields = ("keyword", "trigger_type", "id")


class FlowProtoSerializer(proto_serializers.ModelProtoSerializer):

    triggers = FlowTriggerProtoSerializer(many=True, read_only=True)

    class Meta:
        model = Flow
        proto_class = flow_pb2.Flow
        fields = ["uuid", "name", "triggers"]
