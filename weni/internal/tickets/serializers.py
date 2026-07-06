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
    uuid = serializers.UUIDField(required=False)
    queue_purpose = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        max_length=TicketerQueue.MAX_QUEUE_PURPOSE_LEN,
    )

    class Meta:
        model = TicketerQueue
        fields = ("uuid", "name", "queue_purpose")

    def get_extra_kwargs(self):
        extra_kwargs = super().get_extra_kwargs()
        if self.instance is None:
            extra_kwargs.setdefault("uuid", {})
            extra_kwargs["uuid"]["required"] = True
        return extra_kwargs

    def validate(self, attrs):
        if "uuid" in attrs:
            attrs["queue_uuid"] = attrs.pop("uuid")

        return attrs

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["uuid"] = str(instance.queue_uuid)
        return data

    def create(self, validated_data):
        if "queue_uuid" not in validated_data:
            raise serializers.ValidationError({"uuid": "This field is required."})
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data.pop("queue_uuid", None)
        queue_purpose = validated_data.pop("queue_purpose", serializers.empty)

        instance = super().update(instance, validated_data)

        if queue_purpose is not serializers.empty:
            TicketerQueue.objects.filter(pk=instance.pk).update(queue_purpose=queue_purpose)
            instance.queue_purpose = queue_purpose

        return instance
