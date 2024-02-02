from rest_framework import serializers
from django.contrib.auth import get_user_model

from weni.internal.models import Project
from weni.grpc.core import serializers as weni_serializers


User = get_user_model()


class TemplateOrgSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(write_only=True)
    timezone = serializers.CharField()
    uuid = serializers.UUIDField(read_only=False, required=True)
    flow_organization = serializers.UUIDField(source="uuid", read_only=True)

    class Meta:
        model = Project
        fields = ("user_email", "name", "timezone", "uuid", "flow_organization")

    def validate(self, attrs):
        attrs = dict(attrs)
        user_email = attrs.get("user_email")

        user, _ = User.objects.get_or_create(email=user_email, defaults={"username": user_email})
        attrs["created_by"] = user
        attrs["modified_by"] = user

        attrs.pop("user_email")

        return super().validate(attrs)

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret["uuid"] = instance.project_uuid

        return ret

    def create(self, validated_data):
        validated_data["plan"] = "infinity"
        validated_data["project_uuid"] = validated_data.pop("uuid")

        project = super().create(validated_data)

        project.administrators.add(validated_data.get("created_by"))
        project.initialize(sample_flows=False)

        return project


class OrgSerializer(serializers.ModelSerializer):
    users = serializers.SerializerMethodField()
    timezone = serializers.CharField()
    uuid = serializers.UUIDField(source="project_uuid")
    flow_organization = serializers.UUIDField(source="uuid")

    def set_user_permission(self, user: dict, permission: str) -> dict:
        user["permission_type"] = permission
        return user

    def get_users(self, project: Project):
        values = ["id", "email", "username", "first_name", "last_name"]

        administrators = list(project.administrators.all().values(*values))
        viewers = list(project.viewers.all().values(*values))
        editors = list(project.editors.all().values(*values))
        surveyors = list(project.surveyors.all().values(*values))

        administrators = list(
            map(
                lambda user: self.set_user_permission(user, "administrator"),
                administrators,
            )
        )
        viewers = list(map(lambda user: self.set_user_permission(user, "viewer"), viewers))
        editors = list(map(lambda user: self.set_user_permission(user, "editor"), editors))
        surveyors = list(map(lambda user: self.set_user_permission(user, "surveyor"), surveyors))

        users = administrators + viewers + editors + surveyors

        return users

    class Meta:
        model = Project
        fields = [
            "id",
            "name",
            "uuid",
            "timezone",
            "date_format",
            "users",
            "flow_organization",
        ]


class OrgCreateSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField()

    class Meta:
        model = Project
        fields = ["name", "timezone", "user_email", "uuid"]


class OrgUpdateSerializer(serializers.ModelSerializer):
    project_uuid = serializers.CharField(read_only=True)
    modified_by = weni_serializers.UserEmailRelatedField(required=False, write_only=True)
    timezone = serializers.CharField(required=False)
    name = serializers.CharField(required=False)
    plan_end = serializers.DateTimeField(required=False)

    class Meta:
        model = Project
        fields = [
            "project_uuid",
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


class UpdateProjectSerializer(serializers.ModelSerializer):
    project_uuid = serializers.CharField(read_only=True)
    modified_by = weni_serializers.UserEmailRelatedField(required=False, write_only=True)

    class Meta:
        model = Project
        fields = ["project_uuid", "modified_by"]
