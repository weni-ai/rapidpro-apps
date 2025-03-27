from rest_framework import serializers
from django.contrib.auth import get_user_model

from temba.tickets.models import Ticketer
from weni import serializers as weni_serializers
from weni.internal.models import TicketerQueue


User = get_user_model()


class TicketerConfigSerializer(serializers.Serializer):
    project_auth = serializers.CharField(required=True)
    sector_uuid = serializers.CharField(required=True)


class TicketerSerializer(serializers.ModelSerializer):
    org = weni_serializers.OrgUUIDRelatedField(required=True)
    config = serializers.DictField(required=True)

    class Meta:
        model = Ticketer
        fields = ("uuid", "org", "ticketer_type", "name", "config")
        read_only_fields = ("uuid",)

    def create(self, validated_data):
        user = self.context["request"].user

        validated_data["created_by"] = user
        validated_data["modified_by"] = user

        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        user = self.context["request"].user

        instance.modified_by = user

        if "config" in validated_data:
            instance.config.update(validated_data["config"])
            validated_data["config"] = instance.config

        return super().update(instance, validated_data)


class TicketerQueueSerializer(serializers.ModelSerializer):
    uuid = serializers.UUIDField(required=True)

    class Meta:
        model = TicketerQueue
        fields = ("uuid", "name")
    
    def validate(self, attrs):
        attrs["queue_uuid"] = attrs.pop("uuid")
        return attrs
