from django.contrib.auth.models import User

from rest_framework import serializers

from django_grpc_framework import proto_serializers

from weni.protobuf.flows import user_pb2


class UserPermissionProtoSerializer(proto_serializers.ProtoSerializer):
    administrator = serializers.BooleanField(default=False)
    viewer = serializers.BooleanField(default=False)
    editor = serializers.BooleanField(default=False)
    surveyor = serializers.BooleanField(default=False)
    agent = serializers.BooleanField(default=False)

    class Meta:
        proto_class = user_pb2.Permission


class UserProtoSerializer(proto_serializers.ModelProtoSerializer):
    class Meta:
        model = User
        proto_class = user_pb2.User
        fields = ["id", "email", "username", "first_name", "last_name", "date_joined", "is_active", "is_superuser"]
