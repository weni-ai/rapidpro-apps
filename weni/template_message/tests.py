from django.urls import reverse
from django.contrib.auth.models import Group
from rest_framework import status

from temba.tests import TembaTest
from temba.api.models import APIToken
from temba.templates.models import TemplateTranslation
from temba.channels.models import Channel


class TembaPostRequestMixin:

    url_namespace = None

    def request(self, data: dict = None):
        url = reverse(self.url_namespace)
        token = APIToken.get_or_create(self.org, self.admin, Group.objects.get(name="Administrators"))

        return self.client.post(url, HTTP_AUTHORIZATION=f"Token {token.key}", data=data)


class CreateTemplateMessageTest(TembaPostRequestMixin, TembaTest):

    url_namespace = "api.v2.template_messages"

    def setUp(self):
        super().setUp()

        self.request_data = dict(
            channel=str(self.channel.uuid),
            fb_namespace="36ffbf5c_482f_4943_a0cd_be1412349e74",
            content="Contect test text",
            variable_count=1,
            name="test_name",
            language="por",
            country="BR",
            status="A",
            namespace="weni"
        )

    def test_ok(self):

        data = self.request_data

        response = self.request(data)
        template_translation = TemplateTranslation.objects.first()

        self.assertEquals(response.status_code, status.HTTP_201_CREATED)
        self.assertEquals(template_translation.content, data["content"])
        self.assertEquals(template_translation.variable_count, data["variable_count"])
        self.assertEquals(template_translation.status, data["status"])
        self.assertEquals(template_translation.language, data["language"])
        self.assertEquals(template_translation.country, data["country"])
        self.assertEquals(template_translation.namespace, data["namespace"])

    def test_wrong_channel_uuid(self):
        data = self.request_data
        data["channel"] = "wrong_channel_uuid"

        response = self.request(data)

        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("channel", response.data)
        self.assertEquals(response.data["channel"][0].code, "does_not_exist")
        self.assertEquals(TemplateTranslation.objects.count(), 0)
