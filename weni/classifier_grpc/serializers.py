from django_grpc_framework import proto_serializers

from rest_framework import serializers
from temba.classifiers.models import Classifier
from weni.classifier_grpc.grpc_gen import classifier_pb2


class ClassifierProtoSerializer(proto_serializers.ModelProtoSerializer):

    uuid = serializers.UUIDField(required=True)
    classifier_type = serializers.CharField(required=True)
    name = serializers.CharField(required=True)
    class Meta:
        model = Classifier
        proto_class = classifier_pb2.Classifier
        fields = ["uuid", "classifier_type", "name"]
