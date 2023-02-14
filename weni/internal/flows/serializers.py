from rest_framework import serializers
from django.contrib.auth import get_user_model

from weni.grpc.core import serializers as weni_serializers
from temba.flows.models import Flow


User = get_user_model()


class FlowSerializer(serializers.ModelSerializer):
    project = weni_serializers.ProjectUUIDRelatedField()
    sample_flow = serializers.JSONField(write_only=True)

    class Meta:
        model = Flow
        fields = ("org", "uuid", "sample_flow")

    def create(self, validated_data):
        project = validated_data.get("org")
        sample_flows = validated_data.get("sample_flow")
        project.import_app(sample_flows, project.created_by)
        self.disable_flows_has_issues(project, sample_flows)
        return project.flows.order_by("created_on").last()

    def disable_flows_has_issues(self, org, sample_flows):
        flows_name = list(map(lambda flow: flow.get("name"), sample_flows.get("flows")))
        org.flows.filter(name__in=flows_name).update(has_issues=False)


class FlowListSerializer(serializers.Serializer):
    flow_name = serializers.CharField(required=True, write_only=True)
    org_uuid = weni_serializers.ProjectUUIDRelatedField(required=True, write_only=True)
    uuid = serializers.CharField(read_only=True)
    name = serializers.CharField(read_only=True)
