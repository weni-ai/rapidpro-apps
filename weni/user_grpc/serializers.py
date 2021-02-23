from django_grpc_framework import proto_serializers

from weni.user_grpc.grpc_gen import user_pb2


class OrgProtoSerializer(proto_serializers.Serializer):
    ...