from rest_framework import serializers


from weni.serializers import OrgUUIDRelatedField, UserEmailRelatedField
from temba.externals.models import ExternalService


class ExternalServicesSerializer(serializers.Serializer):
    uuid = serializers.UUIDField(read_only=True)
    type_code = serializers.CharField(write_only=True)
    type_fields = serializers.JSONField(write_only=True)
    org = OrgUUIDRelatedField(write_only=True)
    user = UserEmailRelatedField(write_only=True)

    external_service_type = serializers.CharField(read_only=True)
    name = serializers.CharField(read_only=True)
    config = serializers.JSONField(read_only=True)

    def create(self, validated_data: dict):
        validated_data = validated_data

        type_code = validated_data.get("type_code")
        type_fields = validated_data.get("type_fields")
        user = validated_data.get("user")
        org = validated_data.get("org")

        try:
            type_ = ExternalService.get_type_from_code(type_code)
        except KeyError as error:
            raise serializers.ValidationError(error)

        type_serializer = type_.serializer_class(data=type_fields)
        type_serializer.is_valid(raise_exception=True)
        return type_serializer.save(type=type_, created_by=user, modified_by=user, org=org)
