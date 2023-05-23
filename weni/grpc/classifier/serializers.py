from django_grpc_framework import proto_serializers
from rest_framework import serializers

from temba.classifiers.models import Classifier
from weni.protobuf.flows import classifier_pb2
from weni.grpc.core import serializers as weni_serializers


class ClassifierProtoSerializer(proto_serializers.ModelProtoSerializer):
    uuid = serializers.UUIDField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    classifier_type = serializers.CharField(required=True)
    name = serializers.CharField(required=True)
    access_token = weni_serializers.SerializerMethodCharField(required=True)
    user = weni_serializers.UserEmailRelatedField(write_only=True)
    org = weni_serializers.OrgUUIDRelatedField(write_only=True)

    def get_access_token(self, instance):
        return instance.config.get("access_token")

    def create(self, validated_data: dict) -> Classifier:
        config = dict(access_token=validated_data["access_token"])
        validated_data.pop("access_token")

        return Classifier.create(config=config, **validated_data)

    class Meta:
        model = Classifier
        proto_class = classifier_pb2.Classifier
        fields = [
            "uuid",
            "is_active",
            "classifier_type",
            "name",
            "access_token",
            "org",
            "user",
        ]
