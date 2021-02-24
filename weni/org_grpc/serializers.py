from django.contrib.auth.models import User
from django_grpc_framework import proto_serializers
from rest_framework import serializers

from temba.orgs.models import Org
from weni.org_grpc.grpc_gen import org_pb2


class SerializerUtils(object):
    @classmethod
    def get_object(cls, model, pk: int):
        try:
            return model.objects.get(pk=pk)
        except model.DoesNotExist:
            raise proto_serializers.ValidationError(f"{model.__name__}: {pk} not found!")


class OrgProtoSerializer(proto_serializers.ModelProtoSerializer):

    users = serializers.SerializerMethodField()

    def get_users(self, org: Org):
        users = org.administrators.union(org.viewers.all(), org.editors.all(), org.surveyors.all())
        return list(users.values("id", "email", "username", "first_name", "last_name"))

    class Meta:
        model = Org
        proto_class = org_pb2.Org
        fields = ["id", "name", "uuid", "users"]


class OrgCreateProtoSerializer(proto_serializers.ModelProtoSerializer):

    user_id = serializers.IntegerField()

    def validate_user_id(self, value: int) -> int:
        SerializerUtils.get_object(User, value)

        return value

    def save(self):

        user = User.objects.get(id=self.validated_data.get("user_id"))
        validated_data = {
            "name": self.validated_data.get("name"),
            "timezone": self.validated_data.get("timezone"),
            "created_by": user,
            "modified_by": user,
        }

        Org.objects.create(**validated_data)

    class Meta:
        model = Org
        proto_class = org_pb2.Org
        fields = ["name", "timezone", "user_id"]


class OrgUpdateProtoSerializer(proto_serializers.ModelProtoSerializer):

    id = serializers.IntegerField()
    user_id = serializers.IntegerField()
    timezone = serializers.CharField(required=False)
    name = serializers.CharField(required=False)
    plan_end = serializers.DateTimeField(required=False)

    def validate_id(self, value):
        SerializerUtils.get_object(Org, value)

        return value

    def validate_user_id(self, value):
        SerializerUtils.get_object(User, value)

        return value

    def save(self):
        data = dict(self.validated_data)

        org_qs = Org.objects.filter(pk=data.get("id"))

        org = org_qs.first()
        user = SerializerUtils.get_object(User, data.get("user_id"))

        if not self._user_has_permisson(user, org) and not user.is_superuser:
            raise proto_serializers.ValidationError(f"User: {user.pk} has no permission to update Org: {org.pk}")

        updated_fields = self.get_updated_fields(data)

        if updated_fields:
            org_qs.update(**updated_fields, modified_by=user)

    def get_updated_fields(self, data):
        return {key: value for key, value in data.items() if key not in ["id", "user_id"]}

    def _user_has_permisson(self, user: User, org: Org) -> bool:
        return (
            user.org_admins.filter(pk=org.pk)
            or user.org_viewers.filter(pk=org.pk)
            or user.org_editors.filter(pk=org.pk)
            or user.org_surveyors.filter(pk=org.pk)
        )

    class Meta:
        model = Org
        proto_class = org_pb2.Org
        fields = [
            "id",
            "user_id",
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
