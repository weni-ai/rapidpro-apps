from rest_framework import serializers
from weni import serializers as weni_serializers

from temba.globals.models import Global
from temba.orgs.models import Org


class GlobalSerializer(serializers.ModelSerializer):
    org = weni_serializers.OrgUUIDRelatedField(required=True)
    user = weni_serializers.UserEmailRelatedField(required=True, write_only=True)

    def validate(self, attrs) -> dict:
        # All the logic needs to be recreated because
        # Rapidpro didn't separate the business rule from the view layer

        validated_data = super().validate(attrs)
        org = validated_data.get("org")
        name = validated_data.get("name")

        org_active_globals_limit = org.get_limit(Org.LIMIT_GLOBALS)

        if org.globals.filter(is_active=True).count() >= org_active_globals_limit:
            raise serializers.ValidationError(f"Cannot create a new global as limit is {org_active_globals_limit}.")

        if not Global.is_valid_name(name):
            message = {
                "name": serializers.ErrorDetail("Can only contain letters, numbers and hypens.", code="invalid")
            }
            raise serializers.ValidationError(message)

        if not Global.is_valid_key(Global.make_key(name)):
            message = {"name": serializers.ErrorDetail("Isn't a valid name", code="invalid")}
            raise serializers.ValidationError(message)

        return validated_data

    def create(self, validated_data):
        name = validated_data.get("name")

        return Global.get_or_create(
            validated_data.get("org"),
            validated_data.get("user"),
            key=Global.make_key(name=name),
            value=validated_data.get("value"),
            name=name,
        )

    def create_many(self, validated_data_list):
        for validated_data in validated_data_list:
            name = validated_data.get("name")

            Global.get_or_create(
                validated_data.get("org"),
                validated_data.get("user"),
                key=Global.make_key(name=name),
                value=validated_data.get("value"),
                name=name,
            )

    class Meta:
        model = Global
        fields = ("uuid", "org", "user", "name", "value")
        read_only_fields = ("uuid",)
