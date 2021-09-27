from django.urls import reverse
from rest_framework import status

from temba.tests import TembaTest
from temba.api.models import APIToken
from temba.templates.models import TemplateTranslation
from temba.channels.models import Channel
from temba.channels.types.whatsapp.type import (
    CONFIG_FB_ACCESS_TOKEN,
    CONFIG_FB_BUSINESS_ID,
    CONFIG_FB_NAMESPACE,
    CONFIG_FB_TEMPLATE_LIST_DOMAIN,
)


class TembaPostRequestMixin:

    url_namespace = None

    def request(self, data=None, user=None):
        url = reverse(self.url_namespace)
        token = APIToken.get_or_create(self.org, user if user else self.admin)

        return self.client.post(f"{url}.json", HTTP_AUTHORIZATION=f"Token {token.key}", data=data)


class CreateTemplateMessageTest(TembaPostRequestMixin, TembaTest):

    url_namespace = "api.v2.template_messages"

    def setUp(self):
        super().setUp()
        self.wa_channel = self.create_channel(
            "WA",
            "WhatsApp: 1235",
            "1235",
            config={
                Channel.CONFIG_BASE_URL: "https://nyaruka.com/whatsapp",
                Channel.CONFIG_USERNAME: "temba",
                Channel.CONFIG_PASSWORD: "tembapasswd",
                Channel.CONFIG_AUTH_TOKEN: "authtoken123",
                CONFIG_FB_BUSINESS_ID: "1234",
                CONFIG_FB_ACCESS_TOKEN: "token123",
                CONFIG_FB_NAMESPACE: "my-custom-app",
                CONFIG_FB_TEMPLATE_LIST_DOMAIN: "graph.facebook.com",
            },
        )

        self.request_data = dict(
            channel=str(self.wa_channel.uuid),
            fb_namespace="36ffbf5c_482f_4943_a0cd_be1412349e74",
            namespace="36ffbf5c_482f_4943_a0cd_be1412349e74",
            content="Contect test text",
            variable_count=1,
            name="test_name",
            language="por",
            country="BR",
            status="A",
        )

    def test_admin_create_template(self):

        data = self.request_data

        response = self.request(data)
        template_translation = TemplateTranslation.objects.first()

        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
        self.assertEquals(template_translation.content, data["content"])
        self.assertEquals(template_translation.variable_count, data["variable_count"])
        self.assertEquals(template_translation.status, data["status"])
        self.assertEquals(template_translation.language, data["language"])
        self.assertEquals(template_translation.country, data["country"])
        self.assertEquals(len(template_translation.external_id), 16)

    def test_editor_create_template(self):
        data = self.request_data

        response = self.request(data, self.editor)
        template_translation = TemplateTranslation.objects.first()

        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
        self.assertEquals(template_translation.content, data["content"])
        self.assertEquals(template_translation.variable_count, data["variable_count"])
        self.assertEquals(template_translation.status, data["status"])
        self.assertEquals(template_translation.language, data["language"])
        self.assertEquals(template_translation.country, data["country"])
        self.assertEquals(len(template_translation.external_id), 16)

    def test_create_template_with_non_whatsapp_channel(self):
        data = self.request_data
        data["channel"] = self.channel.uuid

        response = self.request(data)

        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("channel", response.json())

    def test_wrong_channel_uuid(self):
        data = self.request_data
        data["channel"] = "wrong_channel_uuid"

        response = self.request(data)
        data = response.json()

        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("channel", data)
        self.assertEquals(TemplateTranslation.objects.count(), 0)

    def test_create_template_with_token_from_another_org(self):
        another_channel = self.create_channel(
            "WA",
            "WhatsApp: 1235",
            "1235",
            org=self.org2,
            config={
                Channel.CONFIG_BASE_URL: "https://nyaruka.com/whatsapp",
                Channel.CONFIG_USERNAME: "temba",
                Channel.CONFIG_PASSWORD: "tembapasswd",
                Channel.CONFIG_AUTH_TOKEN: "authtoken123",
                CONFIG_FB_BUSINESS_ID: "1234",
                CONFIG_FB_ACCESS_TOKEN: "token123",
                CONFIG_FB_NAMESPACE: "my-custom-app",
                CONFIG_FB_TEMPLATE_LIST_DOMAIN: "graph.facebook.com",
            },
        )

        data = self.request_data
        data["channel"] = str(another_channel.uuid)

        response = self.request(data)
        response_data = response.json()

        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("channel", response_data)

    def test_create_template_without_country(self):
        data = self.request_data.copy()
        data.pop("country")

        self.request(data)
        template_translation = TemplateTranslation.objects.first()
        self.assertIsNone(template_translation.country.code)
