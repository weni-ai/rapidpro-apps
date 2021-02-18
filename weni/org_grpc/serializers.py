from django.contrib.auth.models import User

from rest_framework import serializers

from django_grpc_framework import proto_serializers
import org_pb2

from temba.orgs.models import Org


class OrgProtoSerializer(proto_serializers.ModelProtoSerializer):

    users = serializers.SerializerMethodField()

    def get_users(self, org: Org):
        users = org.administrators.union(
            org.viewers.all(),
            org.editors.all(),
            org.surveyors.all()
        )
        return list(users.values(
            "id", "email", "username", "first_name", "last_name"
        ))

    class Meta:
        model = Org
        proto_class = org_pb2.Org
        fields = ["id", "name", "uuid", "users"]


class OrgCreateProtoSerializer(proto_serializers.ModelProtoSerializer):

    user_id = serializers.IntegerField()

    def validate_user_id(self, value: int) -> int:
        try:
            User.objects.get(id=value)
        except User.DoesNotExist:
            raise proto_serializers.ValidationError("user_id not found!")

        return value

    def save(self):

        user = User.objects.get(id=self.validated_data.get("user_id"))
        validated_data = {
            "name": self.validated_data.get("name"),
            "timezone": self.validated_data.get("timezone"),
            "created_by": user,
            "modified_by": user
        }

        Org.objects.create(**validated_data)

    class Meta:
        model = Org
        proto_class = org_pb2.Org
        fields = ["name", "timezone", "user_id"]
