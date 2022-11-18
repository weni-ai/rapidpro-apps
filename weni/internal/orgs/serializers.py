from rest_framework import serializers
from django.contrib.auth import get_user_model

from temba.orgs.models import Org
from weni.grpc.core import serializers as weni_serializers


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
        org.initialize(sample_flows=False, internal_ticketer=False)

        return org


class OrgSerializer(serializers.ModelSerializer):

    users = serializers.SerializerMethodField()
    timezone = serializers.CharField()

    def set_user_permission(self, user: dict, permission: str) -> dict:
        user["permission_type"] = permission
        return user

    def get_users(self, org: Org):
        values = ["id", "email", "username", "first_name", "last_name"]

        administrators = list(org.administrators.all().values(*values))
        viewers = list(org.viewers.all().values(*values))
        editors = list(org.editors.all().values(*values))
        surveyors = list(org.surveyors.all().values(*values))

        administrators = list(map(lambda user: self.set_user_permission(user, "administrator"), administrators))
        viewers = list(map(lambda user: self.set_user_permission(user, "viewer"), viewers))
        editors = list(map(lambda user: self.set_user_permission(user, "editor"), editors))
        surveyors = list(map(lambda user: self.set_user_permission(user, "surveyor"), surveyors))

        users = administrators + viewers + editors + surveyors

        return users

    class Meta:
        model = Org
        fields = ["id", "name", "uuid", "timezone", "date_format", "users"]


class OrgCreateSerializer(serializers.ModelSerializer):

    user_email = serializers.EmailField()

    class Meta:
        model = Org
        fields = ["name", "timezone", "user_email"]


class OrgUpdateSerializer(serializers.ModelSerializer):

    uuid = serializers.CharField(read_only=True)
    modified_by = weni_serializers.UserEmailRelatedField(required=False, write_only=True)
    timezone = serializers.CharField(required=False)
    name = serializers.CharField(required=False)
    plan_end = serializers.DateTimeField(required=False)

    class Meta:
        model = Org
        fields = [
            "uuid",
            "modified_by",
            "name",
            "timezone",
            "date_format",
            "plan",
            "plan_end",
            "brand",
            "is_anon",
            "is_multi_user",
            "is_multi_org",
            "is_suspended",
        ]
