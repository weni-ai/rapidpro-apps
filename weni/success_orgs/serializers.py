from rest_framework import serializers


class SuccessOrgSerializer(serializers.Serializer):
    uuid = serializers.UUIDField()
    name = serializers.CharField()
    has_ia = serializers.BooleanField()
    has_flows = serializers.BooleanField()
    has_channel = serializers.BooleanField()
    has_msg = serializers.BooleanField()
    is_success_project = serializers.BooleanField()


class UserSuccessOrgSerializer(serializers.Serializer):
    email = serializers.EmailField()
    last_login = serializers.CharField()
    orgs = SuccessOrgSerializer(many=True)
