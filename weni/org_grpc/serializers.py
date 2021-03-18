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
    timezone = serializers.CharField()

    def get_users(self, org: Org):
        users = org.administrators.union(org.viewers.all(), org.editors.all(), org.surveyors.all())
        return list(users.values("id", "email", "username", "first_name", "last_name"))

    class Meta:
        model = Org
        proto_class = org_pb2.Org
        fields = ["id", "name", "uuid", "timezone", "date_format", "users"]


class OrgCreateProtoSerializer(proto_serializers.ModelProtoSerializer):

    user_email = serializers.EmailField()

    class Meta:
        model = Org
        proto_class = org_pb2.Org
        fields = ["name", "timezone", "user_email"]


class OrgUpdateProtoSerializer(proto_serializers.ModelProtoSerializer):

    uuid = serializers.UUIDField()
    user_email = serializers.EmailField()
    timezone = serializers.CharField(required=False)
    name = serializers.CharField(required=False)
    plan_end = serializers.DateTimeField(required=False)

    def validate_id(self, value):
        SerializerUtils.get_object(Org, value)

        return value

    class Meta:
        model = Org
        proto_class = org_pb2.Org
        fields = [
            "uuid",
            "user_email",
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
