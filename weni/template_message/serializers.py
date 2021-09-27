from rest_framework import serializers

from temba.templates.models import TemplateTranslation
from temba.api.v2.serializers import WriteSerializer
from temba.channels.types.whatsapp.type import WhatsAppType
from temba.channels.types.dialog360 import Dialog360Type
from temba.api.v2 import fields


class TemplateMessageSerializers(WriteSerializer):

    channel = fields.ChannelField()
    content = serializers.CharField()
    name = serializers.CharField(write_only=True)
    language = serializers.CharField()
    country = serializers.CharField(default=None)
    variable_count = serializers.IntegerField()
    status = serializers.CharField()

    fb_namespace = serializers.CharField(required=False, write_only=True)
    namespace = serializers.CharField(required=True)

    def validate_channel(self, channel):
        if channel.channel_type not in [WhatsAppType.code, Dialog360Type.code]:
            raise serializers.ValidationError("Template messages can be created only for WhatsApp channels")

        return channel

    def save(self) -> TemplateTranslation:
        validated_data = self.validated_data

        fb_namespace = validated_data.get("fb_namespace")
        channel = validated_data["channel"]

        if fb_namespace:
            channel.config["fb_namespace"] = fb_namespace
            channel.save()
            validated_data.pop("fb_namespace")

        validated_data["external_id"] = self.external_id

        template_translation = TemplateTranslation.get_or_create(**validated_data)

        return template_translation

    @property
    def external_id(self):
        from django.utils.crypto import get_random_string
        from string import digits

        return get_random_string(16, digits)

    class Meta:
        model = TemplateTranslation
        fields = [
            "channel",
            "content",
            "name",
            "language",
            "country",
            "variable_count",
            "status",
            "fb_namespace",
            "namespace",
        ]
