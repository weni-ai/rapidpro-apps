from django.contrib.auth import get_user_model

from rest_framework import serializers

from weni.serializers import fields as weni_serializers

User = get_user_model()


class UserAPITokenSerializer(serializers.Serializer):
    user = weni_serializers.UserEmailRelatedField(required=True)
    project = weni_serializers.ProjectUUIDRelatedField(required=True)


class UserPermissionSerializer(serializers.Serializer):
    administrator = serializers.BooleanField(default=False)
    viewer = serializers.BooleanField(default=False)
    editor = serializers.BooleanField(default=False)
    surveyor = serializers.BooleanField(default=False)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "username", "first_name", "last_name", "date_joined", "is_active", "is_superuser"]
