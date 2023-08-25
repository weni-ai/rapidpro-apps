from rest_framework import serializers
from temba.externals.models import Prompt

from weni.serializers import UserEmailRelatedField
from temba.externals.models import ExternalService
from weni.serializers.fields import ProjectUUIDRelatedField


AI_MODELS = [
    ("gpt-3.5-turbo-16k", "gpt-3.5-turbo-16k"),
    ("gpt-3.5-turbo", "gpt-3.5-turbo"),
    ("gpt-4", "gpt-4"),
]


class ExternalServicesSerializer(serializers.Serializer):
    uuid = serializers.UUIDField(read_only=True)
    type_code = serializers.CharField(write_only=True)
    type_fields = serializers.JSONField(write_only=True)
    project = ProjectUUIDRelatedField(write_only=True)
    user = UserEmailRelatedField(write_only=True)

    external_service_type = serializers.CharField(read_only=True)
    name = serializers.CharField(read_only=True)
    config = serializers.JSONField(read_only=True)

    def create(self, validated_data: dict):
        type_code = validated_data.get("type_code")
        type_fields = validated_data.get("type_fields")
        user = validated_data.get("user")
        project = validated_data.get("project")

        try:
            type_ = ExternalService.get_type_from_code(type_code)
        except KeyError as error:
            raise serializers.ValidationError(error)

        type_serializer = type_.serializer_class(data=type_fields)
        type_serializer.is_valid(raise_exception=True)
        return type_serializer.save(
            type=type_, created_by=user, modified_by=user, org=project
        )


class UpdateExternalServicesSerializer(serializers.Serializer):
    config = serializers.JSONField()

    def validate(self, attrs):
        config = attrs.get("config")
        if config:
            ai_model = config.get("ai_model")
            if ai_model and ai_model not in [choice[0] for choice in AI_MODELS]:
                raise serializers.ValidationError(f"{ai_model} is a invalid A.I Model")

        return attrs

    def update(self, instance, validated_data: dict):
        instance.config = validated_data.get("config", instance.config)
        instance.save()
        return instance


class PromptSerializer(serializers.Serializer):
    uuid = serializers.UUIDField(read_only=True)
    user = UserEmailRelatedField(write_only=True)
    text = serializers.CharField()

    def create(self, validated_data):
        user = validated_data.pop("user")
        return Prompt.objects.create(created_by=user, modified_by=user, **validated_data)
