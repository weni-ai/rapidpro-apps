from django_grpc_framework import proto_serializers
import org_pb2

from temba.orgs.models import Org

class OrgProtoSerializer(proto_serializers.ModelProtoSerializer):
    class Meta:
        model = Org
        proto_class = org_pb2.Org
        fields = ['id', 'name', 'uuid']