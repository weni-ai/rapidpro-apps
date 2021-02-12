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