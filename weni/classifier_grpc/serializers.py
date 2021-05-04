from django_grpc_framework import proto_serializers

from rest_framework import serializers
from temba.classifiers.models import Classifier
from weni.classifier_grpc.grpc_gen import classifier_pb2
from weni.grpc_central.serializers import SerializerUtils


class ClassifierProtoSerializer(proto_serializers.ModelProtoSerializer):

    uuid = serializers.UUIDField(read_only=True)
    classifier_type = serializers.CharField(required=True)
    name = serializers.CharField(required=True)
    org_uuid = serializers.CharField(write_only=True)
    user_email = serializers.EmailField(write_only=True)

    def create(self, validated_data: dict) -> Classifier:
        user = SerializerUtils.get_user_object(validated_data["user_email"], "email")
        org = SerializerUtils.get_org_object(validated_data["org_uuid"], "uuid")

        validated_data.pop("org_uuid")
        validated_data.pop("user_email")

        data = validated_data
        data["org"] = org
        data["user"] = user
        data["config"] = {}

        return Classifier.create(**data, sync=False)

    class Meta:
        model = Classifier
        proto_class = classifier_pb2.Classifier
        fields = ["uuid", "classifier_type", "name", "org_uuid", "user_email"]
