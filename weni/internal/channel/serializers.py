import re

from django.http.response import HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.messages.middleware import MessageMiddleware
from django.shortcuts import get_object_or_404
from django.test import RequestFactory

from rest_framework import serializers
from rest_framework import exceptions

from weni.grpc.core import serializers as weni_serializers

from temba.channels.models import Channel
from temba.orgs.models import Org
from temba.utils import analytics


class ChannelWACSerializer(serializers.Serializer):
    user = weni_serializers.UserEmailRelatedField(required=True, write_only=True)
    org = weni_serializers.OrgUUIDRelatedField(required=True, write_only=True)
    phone_number_id = serializers.CharField(required=True, write_only=True)
    uuid = serializers.CharField(read_only=True)
    name = serializers.CharField(read_only=True)
    address = serializers.CharField(read_only=True)
    config = serializers.JSONField(required=True)

    class Meta:
        model = Channel
        proto_class = Channel
        fields = ("user", "org", "phone_number_id", "uuid", "name", "address", "config")

    def validate_phone_number_id(self, value):
        if Channel.objects.filter(is_active=True, address=value).exists():
            raise serializers.ValidationError(
                {
                    "error": "a Channel with that 'phone_number_id' alredy exists",
                    "error_type": "WhatsApp.config.error.channel_already_exists",
                }
            )
        return value

    def validate_config(self, value):
        if "wa_verified_name" not in value:
            raise serializers.ValidationError({"error": "You need to define a wa_verified_name in config"})
        return value

    def create(self, validated_data):
        channel_type = Channel.get_type_from_code("WAC")
        schemes = channel_type.schemes

        org = validated_data.get("org")
        name = validated_data.get("name")
        phone_number_id = validated_data.get("phone_number_id")
        config = validated_data.get("config", {})
        user = validated_data.get("user")

        channel = Channel.objects.create(
            org=org,
            country=None,
            channel_type=channel_type.code,
            name=config.get("wa_verified_name"),
            address=phone_number_id,
            config=config,
            role=Channel.DEFAULT_ROLE,
            schemes=schemes,
            created_by=user,
            modified_by=user,
        )

        analytics.track(user, "temba.channel_created", dict(channel_type=channel_type.code))

        return channel


class CreateChannelSerializer(serializers.Serializer):
    uuid = serializers.CharField(read_only=True)
    name = serializers.CharField(read_only=True)
    config = serializers.JSONField(read_only=True)
    address = serializers.CharField(read_only=True)

    user = serializers.EmailField(required=True, write_only=True)
    org = serializers.CharField(required=True, write_only=True)
    data = serializers.JSONField(write_only=True)
    channeltype_code = serializers.CharField(required=True, write_only=True)

    def create(self, validated_data):
        data = validated_data.get("data")

        user = get_object_or_404(User, email=validated_data.get("user"))
        org = get_object_or_404(Org, uuid=validated_data.get("org"))

        channel_type = Channel.get_type_from_code(validated_data.get("channeltype_code"))

        if channel_type is None:
            channel_type_code = validated_data.get("channeltype_code")
            raise exceptions.ValidationError(f"No channels found with '{channel_type_code}' code")

        url = self.create_channel(user, org, data, channel_type)

        if url is None:
            raise exceptions.ValidationError(f"Url not created")

        if "/users/login/?next=" in url:
            raise exceptions.ValidationError(f"User: {user.email} do not have permission in Org: {org.uuid}")

        regex = "[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12}"
        channe_uuid = re.findall(regex, url)[0]
        channel = Channel.objects.get(uuid=channe_uuid)

        return channel

    def create_channel(self, user: User, org: Org, data: dict, channel_type) -> str:
        factory = RequestFactory()
        url = f"channels/types/{channel_type.slug}/claim"

        request = factory.post(url, data)
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()

        user._org = org
        request.user = user
        response = MessageMiddleware(channel_type.claim_view.as_view(channel_type=channel_type))(request)

        if isinstance(response, HttpResponseRedirect):
            return response.url


class ChannelSerializer(serializers.ModelSerializer):
    config = serializers.JSONField()

    class Meta:
        extra_kwargs = {
            'org': {'read_only': True},
            'is_active': {'read_only': True},
        }
        model = Channel
        fields = (
            "uuid",
            "name",
            "config",
            "address",
            "org",
            "is_active",
        ) 

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['org'] = instance.uuid
        return ret
