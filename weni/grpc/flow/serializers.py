from weni.protobuf.flows import flow_pb2

from django_grpc_framework import proto_serializers

from temba.flows.models import Flow


class FlowProtoSerializer(proto_serializers.ModelProtoSerializer):
    class Meta:
        model = Flow
        proto_class = flow_pb2.Flow
        fields = ["uuid", "name"]
