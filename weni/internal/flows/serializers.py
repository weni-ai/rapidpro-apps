from rest_framework import serializers
from django.contrib.auth import get_user_model

from weni.grpc.core import serializers as weni_serializers
from temba.flows.models import Flow


User = get_user_model()


class FlowSerializer(serializers.ModelSerializer):

    org = weni_serializers.OrgUUIDRelatedField()
    sample_flow = serializers.JSONField(write_only=True)

    class Meta:
        model = Flow
        fields = ("org", "uuid", "sample_flow")

    def create(self, validated_data):
        org = validated_data.get("org")
        sample_flows = validated_data.get("sample_flow")

        org.import_app(sample_flows, org.created_by)

        return org.flows.order_by("created_on").last()
