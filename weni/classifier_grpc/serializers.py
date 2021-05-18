from django_grpc_framework import proto_serializers
from rest_framework import serializers

from temba.classifiers.models import Classifier
from weni.classifier_grpc.grpc_gen import classifier_pb2
from weni.grpc_central import serializers as weni_serializers


class ClassifierProtoSerializer(proto_serializers.ModelProtoSerializer):

    uuid = serializers.UUIDField(read_only=True)
    classifier_type = serializers.CharField(required=True)
    name = serializers.CharField(required=True)
    user = weni_serializers.UserEmailRelatedField(write_only=True)
    org = weni_serializers.OrgUUIDRelatedField(write_only=True)

    def create(self, validated_data: dict) -> Classifier:
        return Classifier.create(config={}, **validated_data)

    class Meta:
        model = Classifier
        proto_class = classifier_pb2.Classifier
        fields = ["uuid", "classifier_type", "name", "org", "user"]
