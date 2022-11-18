import json
from abc import ABC, abstractmethod
from uuid import uuid1
from unittest.mock import patch

from django.contrib.auth.models import Group
from django.urls import reverse
from django.utils import timezone as tz
from django.utils.http import urlencode
from django.contrib.auth.models import User

from temba.api.models import APIToken

from temba.flows.models import Flow
from temba.orgs.models import Org, OrgRole
from temba.contacts.models import Contact
from temba.channels.models import Channel

from temba.tests import TembaTest, mock_mailroom
 

class TembaRequestMixin(ABC):
    def reverse(self, viewname, kwargs=None, query_params=None):
        url = reverse(viewname, kwargs=kwargs)

        if query_params:
            return "%s?%s" % (url, urlencode(query_params))
        else:
            return url

    def request_get(self, **query_params):
        url = self.reverse(self.get_url_namespace(), query_params=query_params)
        token = APIToken.get_or_create(self.org, self.admin, Group.objects.get(name="Administrators"))

        return self.client.get(f"{url}", HTTP_AUTHORIZATION=f"Token {token.key}")

    def request_detail(self, uuid):
        url = self.reverse(self.get_url_namespace(), kwargs={"uuid": uuid})
        token = APIToken.get_or_create(self.org, self.admin, Group.objects.get(name="Administrators"))

        return self.client.get(f"{url}", HTTP_AUTHORIZATION=f"Token {token.key}")

    def request_post(self, data):
        url = reverse(self.get_url_namespace())
        token = APIToken.get_or_create(self.org, self.admin, Group.objects.get(name="Administrators"))

        return self.client.post(
            url, HTTP_AUTHORIZATION=f"Token {token.key}", data=json.dumps(data), content_type="application/json"
        )

    def request_delete(self, uuid):
        url = self.reverse(self.get_url_namespace(), kwargs={"uuid": uuid})
        token = APIToken.get_or_create(self.org, self.admin, Group.objects.get(name="Administrators"))

        return self.client.delete(f"{url}", HTTP_AUTHORIZATION=f"Token {token.key}")

    @abstractmethod
    def get_url_namespace(self):
        ...


class CreateWACServiceTest(TembaTest, TembaRequestMixin):
    def setUp(self):
        self.user = User.objects.create_user(username="fake@weni.ai", password="123", email="fake@weni.ai")
        self.org = Org.objects.create(
            name="Weni", timezone="America/Sao_Paulo", created_by=self.user, modified_by=self.user
        )
        self.org.add_user(self.user, OrgRole.ADMINISTRATOR)

        self.config = {
            "wa_number": "5561995743921",
            "wa_verified_name": "Weni Test",
            "wa_waba_id": "2433443436435435",
            "wa_currency": "USD",
            "wa_business_id": "3443243234254322",
            "wa_message_template_namespace": "6b186dea_ds6d_44s2_b9xd_de87a12212e5",
        }

        super().setUp()

    @patch("temba.channels.types.whatsapp_cloud.type.WhatsAppCloudType.activate")
    def test_create_whatsapp_cloud_channel(self, mock):
        mock.return_value = None

        phone_number_id = "5426423432"

        payload = {
            "org": str(self.org.uuid),
            "user": self.user.email,
            "phone_number_id": phone_number_id,
            "config": self.config,
        }

        channel = self.request_post(data=payload).json()

        self.assertTrue("uuid" in channel)
        self.assertEqual(channel.get("name"), self.config.get("wa_verified_name"))
        self.assertEqual(channel.get("config"), self.config)
        self.assertEqual(channel.get("address"), phone_number_id)

    @patch("temba.channels.types.whatsapp_cloud.type.WhatsAppCloudType.activate")
    def test_create_whatsapp_cloud_channel_invalid_address(self, mock):
        mock.return_value = None

        phone_number_id = "5426423432"

        payload = {
            "org": str(self.org.uuid),
            "user": self.user.email,
            "phone_number_id": phone_number_id,
            "config": self.config,
        }

        self.request_post(data=payload)

        channel = self.request_post(data=payload)

        self.assertEqual(channel.status_code, 400)
        self.assertEqual(
            channel.json().get("phone_number_id").get("error_type"), "WhatsApp.config.error.channel_already_exists"
        )

    def get_url_namespace(self):
        return "channel-create-wac"


class ReleaseChannelTestCase(TembaTest, TembaRequestMixin):
    def setUp(self):
        self.org_user = User.objects.create_user(username="testuser", password="123", email="test@weni.ai")
        self.my_org = Org.objects.create(
            name="Weni", timezone="Africa/Kigali", created_by=self.org_user, modified_by=self.org_user
        )

        super().setUp()

        self.channel_obj = Channel.create(self.my_org, self.org_user, None, "WWC", "Test WWC")

    def test_released_channel_is_active_equal_to_false(self):
        self.request_delete(uuid=str(self.channel_obj.uuid))
        self.assertFalse(Channel.objects.get(id=self.channel_obj.id).is_active)

    def get_url_namespace(self):
        return "channel-detail"


class CreateChannelTestCase(TembaTest, TembaRequestMixin):
    def setUp(self):
        self.org_user = User.objects.create_user(username="fake@weni.ai", password="123", email="fake@weni.ai")
        self.my_org = Org.objects.create(
            name="Weni", timezone="America/Sao_Paulo", created_by=self.org_user, modified_by=self.org_user
        )
        self.my_org.add_user(self.org_user, OrgRole.ADMINISTRATOR)

        super().setUp()

    def test_create_weni_web_chat_channel(self):
        payload = {
            "user": self.org_user.email,
            "org": str(self.my_org.uuid),
            "data": {"name": "test", "base_url": "https://weni.ai"},
            "channeltype_code": "WWC",
        }

        response = self.request_post(data=payload).json()

        print(response)

        channel = Channel.objects.get(uuid=response.get("uuid"))
        self.assertEqual(channel.address, response.get("address"))
        self.assertEqual(channel.name, response.get("name"))
        self.assertEqual(channel.config.get("base_url"), "https://weni.ai")
        self.assertEqual(channel.org, self.my_org)
        self.assertEqual(channel.created_by, self.org_user)
        self.assertEqual(channel.modified_by, self.org_user)
        self.assertEqual(channel.channel_type, "WWC")

    def get_url_namespace(self):
        return "channel-list"


class RetrieveChannelTestCase(TembaTest, TembaRequestMixin):
    def setUp(self):
        self.user = User.objects.create_user(username="fake@weni.ai", password="123", email="fake@weni.ai")
        self.org = Org.objects.create(
            name="Weni", timezone="America/Sao_Paulo", created_by=self.user, modified_by=self.user
        )

        super().setUp()

        self.channel_obj = Channel.create(
            self.org, self.user, None, "WWC", "Test WWC", "test", {"fake_key": "fake_value"}
        )

    def test_channel_retrieve_returned_fields(self):
        response = self.request_detail(uuid=str(self.channel_obj.uuid)).json()

        self.assertEqual(response.get("name"), self.channel_obj.name)
        self.assertEqual(response.get("address"), self.channel_obj.address)
        self.assertEqual(response.get("config"), self.channel_obj.config)

    def get_url_namespace(self):
        return "channel-detail"


class ListChannelTestCase(TembaTest, TembaRequestMixin):
    def setUp(self):
        self.admin = User.objects.create_user(
            username="testuseradmin", password="123", email="test@weni.ai", is_superuser=True
        )
        self.user = User.objects.create_user(username="fake@weni.ai", password="123", email="fake@weni.ai")
        self.orgs = [
            Org.objects.create(
                name=f"Org {org}", timezone="America/Sao_Paulo", created_by=self.user, modified_by=self.user
            )
            for org in range(2)
        ]

        for channel in range(6):
            Channel.create(
                self.orgs[0] if channel % 2 == 0 else self.orgs[1],
                self.user,
                None,
                "WWC" if channel % 2 == 0 else "VK",
                f"Test {channel}",
                "test",
                {},
            )

        super().setUp()

    def test_list_all_channels(self):
        response = self.request_get().json()
        self.assertEqual(len(response), 7)

    def test_list_channels_filtered_by_type(self):
        response = self.request_get(channel_type="WWC").json()
        self.assertEqual(len(response), 3)

    def test_list_channels_filtered_by_org_uuid(self):
        org_uuid = str(self.orgs[0].uuid)
        response = self.request_get(org=org_uuid).json()
        self.assertEqual(len(response), 3)

        channel = Channel.objects.get(uuid=response[0].get("uuid"))
        self.assertEqual(channel.org, self.orgs[0])

    def get_url_namespace(self):
        return "channel-list"
