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
    project = weni_serializers.ProjectUUIDRelatedField(write_only=True, required=True)
    config = serializers.DictField(required=True)

    class Meta:
        model = Ticketer
        fields = ("uuid", "project", "ticketer_type", "name", "config")
        read_only_fields = ("uuid",)

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret["project"] = str(instance.org.proj_uuid) if instance.org else None
        return ret

    def create(self, validated_data):
        user = self.context["request"].user
        org = validated_data.pop("project")
        
        validated_data["org"] = org

        validated_data["created_by"] = user
        validated_data["modified_by"] = user

        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        user = self.context["request"].user

        if "project" in validated_data:
            instance.org = validated_data.pop("project")

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
        if "uuid" in attrs:
            attrs["queue_uuid"] = attrs.pop("uuid")

        return attrs
