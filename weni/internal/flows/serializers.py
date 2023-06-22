from rest_framework import serializers
from django.contrib.auth import get_user_model

from weni.serializers import fields as weni_fields

User = get_user_model()


class FlowSerializer(serializers.Serializer):
    project = weni_fields.ProjectUUIDRelatedField(required=True, write_only=True)
    sample_flow = serializers.JSONField(write_only=True)
    uuid = serializers.UUIDField(read_only=True)

    class Meta:
        fields = ("project", "uuid", "sample_flow")

    def create(self, validated_data):
        project = validated_data.get("project")
        sample_flows = validated_data.get("sample_flow")
        project.import_app(sample_flows, project.created_by)
        self.disable_flows_has_issues(project, sample_flows)
        return project.flows.order_by("created_on").last()

    def disable_flows_has_issues(self, project, sample_flows):
        flows_name = list(map(lambda flow: flow.get("name"), sample_flows.get("flows")))
        project.flows.filter(name__in=flows_name).update(has_issues=False)


class FlowListSerializer(serializers.Serializer):
    flow_name = serializers.CharField(required=True, write_only=True)
    project = weni_fields.ProjectUUIDRelatedField(required=True, write_only=True)
    uuid = serializers.CharField(read_only=True)
    name = serializers.CharField(read_only=True)
