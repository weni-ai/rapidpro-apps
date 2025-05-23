from rest_framework import serializers

from temba.classifiers.models import Classifier
from weni.grpc.core import serializers as weni_serializers


class ClassifierSerializer(serializers.Serializer):
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

        classifier = Classifier.create(config=config, sync=False, **validated_data)
        classifier.sync()

        return classifier

    class Meta:
        model = Classifier
        fields = [
            "uuid",
            "is_active",
            "classifier_type",
            "name",
            "access_token",
            "org",
            "user",
        ]


class ClassifierDeleteSerializer(serializers.Serializer):
    uuid = serializers.UUIDField(required=True)
    user = weni_serializers.UserEmailRelatedField(required=True)
