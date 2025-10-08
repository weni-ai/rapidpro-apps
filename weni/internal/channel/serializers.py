import re

from django.http.response import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.contrib.auth.models import User
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.messages.middleware import MessageMiddleware
from django.shortcuts import get_object_or_404
from django.test import RequestFactory
from django.conf import settings

from rest_framework import serializers
from rest_framework import exceptions

from weni.serializers import fields as weni_serializers

from temba.channels.models import Channel
from temba.utils import analytics
from weni.internal.models import Project
from weni.success_orgs.business import user_has_org_permission


class ChannelWACSerializer(serializers.Serializer):
    user = weni_serializers.UserEmailRelatedField(required=True, write_only=True)
    org = weni_serializers.ProjectUUIDRelatedField(required=True, write_only=True)
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
        if str(value) == str(settings.ROUTER_PHONE_NUMBER_ID):
            return value

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

        org = validated_data["org"].org
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
            tps=80,
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
        org = get_object_or_404(Project, project_uuid=validated_data.get("org"))

        channel_type = Channel.get_type_from_code(validated_data.get("channeltype_code"))

        if channel_type is None:
            channel_type_code = validated_data.get("channeltype_code")
            raise exceptions.ValidationError(f"No channels found with '{channel_type_code}' code")

        url, form_errors = self.create_channel(user, org.org, data, channel_type)

        if url is None:
            if form_errors:
                # Surface the exact validation errors returned by the claim form in a standardized envelope
                raise exceptions.ValidationError({"errors": form_errors})
            raise exceptions.ValidationError({"errors": {"non_field_errors": ["Url not created"]}})

        if "/users/login/?next=" in url:
            raise exceptions.ValidationError({"permission": [f"User {user.email} is not allowed to create channel in org {org.org.uuid}"]})

        regex = "[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12}"
        channe_uuid = re.findall(regex, url)[0]
        channel = Channel.objects.get(uuid=channe_uuid)

        return channel

    def create_channel(self, user: User, org: Project, data: dict, channel_type):
        factory = RequestFactory()
        url = f"channels/types/{channel_type.slug}/claim"

        request = factory.post(url, data)
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()

        if not user_has_org_permission(user, org):
            org.administrators.add(user)

        user._org = org
        request.user = user
        response = MessageMiddleware(channel_type.claim_view.as_view(channel_type=channel_type))(request)

        if isinstance(response, HttpResponseRedirect):
            return response.url, None

        # Attempt to extract detailed form errors when the claim view doesn't redirect
        return None, self._extract_form_errors_from_response(response)

    def _extract_form_errors_from_response(self, response):
        """
        Tries to extract Django form errors from a TemplateResponse returned by a claim view.
        Returns a dict mapping field names to a list of error messages. Includes '__all__' for non-field errors.
        If errors cannot be extracted, returns None.
        """
        try:
            context_data = getattr(response, "context_data", None)
        except Exception:
            context_data = None

        if not context_data:
            return None

        form = context_data.get("form") if isinstance(context_data, dict) else None
        if not form or not hasattr(form, "errors"):
            return None

        errors_dict = {}
        try:
            form_errors = form.errors
            # Prefer structured JSON data when available
            if hasattr(form_errors, "get_json_data"):
                json_data = form_errors.get_json_data()
                for field_name, field_errors in json_data.items():
                    messages = []
                    if isinstance(field_errors, list):
                        for err in field_errors:
                            message = err.get("message") if isinstance(err, dict) else str(err)
                            if message:
                                messages.append(message)
                    if messages:
                        errors_dict[field_name] = messages
            else:
                # Fallback to a simple stringification of errors
                for field_name, field_errors in form_errors.items():
                    messages = [str(e) for e in field_errors]
                    if messages:
                        errors_dict[field_name] = messages
        except Exception:
            return None

        # Normalize common non-field error key from Django forms
        if "__all__" in errors_dict:
            errors_dict["non_field_errors"] = errors_dict.pop("__all__")

        return errors_dict or None


class ChannelSerializer(serializers.ModelSerializer):
    config = serializers.JSONField()

    class Meta:
        extra_kwargs = {
            "org": {"read_only": True},
            "is_active": {"read_only": True},
        }
        model = Channel
        fields = (
            "uuid",
            "name",
            "config",
            "address",
            "org",
            "is_active",
            "channel_type",
        )

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret["org"] = instance.org.project.project_uuid if hasattr(instance.org, "project") else None

        return ret
