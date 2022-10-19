from rest_framework import serializers
from django.contrib.auth import get_user_model

from temba.orgs.models import Org


User = get_user_model()


class TemplateOrgSerializer(serializers.ModelSerializer):

    user_email = serializers.EmailField(write_only=True)
    timezone = serializers.CharField()

    class Meta:
        model = Org
        fields = ("user_email", "name", "timezone", "uuid")
        read_only_fields = ("uuid",)

    def validate(self, attrs):
        attrs = dict(attrs)
        user_email = attrs.get("user_email")

        user, _ = User.objects.get_or_create(email=user_email, defaults={"username": user_email})
        attrs["created_by"] = user
        attrs["modified_by"] = user

        attrs.pop("user_email")

        return super().validate(attrs)

    def create(self, validated_data):
        validated_data["plan"] = "infinity"

        org = super().create(validated_data)

        org.administrators.add(validated_data.get("created_by"))
        org.initialize(sample_flows=False)

        return org
