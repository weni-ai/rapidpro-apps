from django.conf import settings

from rest_framework import serializers
from rest_framework.serializers import ValidationError

from weni.grpc.core import serializers as weni_serializers


class UserAPITokenSerializer(serializers.Serializer):
    user = weni_serializers.UserEmailRelatedField(required=True)
    org = weni_serializers.OrgUUIDRelatedField(required=True)


class UserPermissionSerializer(serializers.Serializer):
    administrator = serializers.BooleanField(default=False)
    viewer = serializers.BooleanField(default=False)
    editor = serializers.BooleanField(default=False)
    surveyor = serializers.BooleanField(default=False)


class UserSerializer(serializers.Serializer):

    id = serializers.IntegerField(read_only=True)
    language = serializers.CharField(write_only=True)

    def update(self, instance, validated_data):
        if validated_data.get("language") not in [language[0] for language in settings.LANGUAGES]:
            raise ValidationError("Invalid argument: language")

        user_settings = instance.get_settings()
        user_settings.language = validated_data.get("language")
        user_settings.save()

        return instance
