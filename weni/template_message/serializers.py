from rest_framework import serializers
from rest_framework import relations

from temba.templates.models import TemplateTranslation
from temba.channels.models import Channel
from temba.api.v2.serializers import WriteSerializer


class TemplateMessageSerializers(WriteSerializer):

    channel = relations.SlugRelatedField(
        slug_field="uuid",
        queryset=Channel.objects.filter(is_active=True)
    )
    content = serializers.CharField()
    name = serializers.CharField(write_only=True)
    language = serializers.CharField()
    country = serializers.CharField()
    variable_count = serializers.IntegerField()
    status = serializers.CharField()
    namespace = serializers.CharField(required=True)

    fb_namespace = serializers.CharField(required=False, write_only=True)

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
        return "KcwEjeofLSDKWDm2i"

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
            "namespace"
        ]
