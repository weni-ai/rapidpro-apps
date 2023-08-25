import json
from abc import ABC, abstractmethod
from unittest.mock import patch
from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework import status

from django.contrib.auth.models import Group
from django.urls import reverse
from django.utils.http import urlencode
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

from temba.api.models import APIToken
from temba.orgs.models import OrgRole
from temba.channels.models import Channel
from temba.channels.types import TYPES
from temba.tests import TembaTest
from weni.internal.models import Project

from .views import AvailableChannels, ChannelEndpoint

view_class = ChannelEndpoint
view_class.permission_classes = []


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
        token = APIToken.get_or_create(self.project, self.admin, Group.objects.get(name="Administrators"))

        return self.client.post(
            url,
            HTTP_AUTHORIZATION=f"Token {token.key}",
            data=json.dumps(data),
            content_type="application/json",
        )

    def request_delete(self, uuid, **query_params):
        url = self.reverse(self.get_url_namespace(), kwargs={"uuid": uuid}, query_params=query_params)
        token = APIToken.get_or_create(self.org, self.admin, Group.objects.get(name="Administrators"))

        return self.client.delete(f"{url}", HTTP_AUTHORIZATION=f"Token {token.key}")

    @abstractmethod
    def get_url_namespace(self):
        ...


class CreateWACServiceTest(TembaTest, TembaRequestMixin):
    def setUp(self):
        self.user = User.objects.create_user(username="fake@weni.ai", password="123", email="fake@weni.ai")
        self.project = Project.objects.create(
            name="Weni",
            timezone="America/Sao_Paulo",
            created_by=self.user,
            modified_by=self.user,
        )
        self.project.add_user(self.user, OrgRole.ADMINISTRATOR)

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
            "org": str(self.project.project_uuid),
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
            "org": str(self.project.project_uuid),
            "user": self.user.email,
            "phone_number_id": phone_number_id,
            "config": self.config,
        }

        self.request_post(data=payload)

        channel = self.request_post(data=payload)

        self.assertEqual(channel.status_code, 400)
        self.assertEqual(
            channel.json().get("phone_number_id").get("error_type"),
            "WhatsApp.config.error.channel_already_exists",
        )

    def get_url_namespace(self):
        return "channel-create-wac"


class ReleaseChannelTestCase(TembaTest, TembaRequestMixin):
    def setUp(self):
        self.org_user = User.objects.create_user(username="testuser", password="123", email="test@weni.ai")
        self.my_org = Project.objects.create(
            name="Weni",
            timezone="Africa/Kigali",
            created_by=self.org_user,
            modified_by=self.org_user,
        )

        super().setUp()
        self.channel_obj = Channel.create(self.my_org.org, self.org_user, None, "WWC", "Test WWC")

    def test_released_channel_is_active_equal_to_false(self):
        response = self.request_delete(uuid=str(self.channel_obj.uuid), user=self.org_user.email)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Channel.objects.get(id=self.channel_obj.id).is_active)

    def get_url_namespace(self):
        return "channel-detail"


class CreateChannelTestCase(TembaTest, TembaRequestMixin):
    def setUp(self):
        self.org_user = User.objects.create_user(username="fake@weni.ai", password="123", email="fake@weni.ai")
        self.project = Project.objects.create(
            name="Weni",
            timezone="America/Sao_Paulo",
            created_by=self.org_user,
            modified_by=self.org_user,
        )
        self.project.add_user(self.org_user, OrgRole.ADMINISTRATOR)

        super().setUp()

    def test_create_weni_web_chat_channel(self):
        payload = {
            "user": self.org_user.email,
            "org": str(self.project.project_uuid),
            "data": {"name": "test", "base_url": "https://weni.ai"},
            "channeltype_code": "WWC",
        }

        response = self.request_post(data=payload).json()

        channel = Channel.objects.get(uuid=response.get("uuid"))
        self.assertEqual(channel.address, response.get("address"))
        self.assertEqual(channel.name, response.get("name"))
        self.assertEqual(channel.config.get("base_url"), "https://weni.ai")
        self.assertEqual(channel.org, self.project.org)
        self.assertEqual(channel.created_by, self.org_user)
        self.assertEqual(channel.modified_by, self.org_user)
        self.assertEqual(channel.channel_type, "WWC")

    def get_url_namespace(self):
        return "channel-list"


class RetrieveChannelTestCase(TembaTest, TembaRequestMixin):
    def setUp(self):
        self.user = User.objects.create_user(username="fake@weni.ai", password="123", email="fake@weni.ai")
        self.project = Project.objects.create(
            name="Weni",
            timezone="America/Sao_Paulo",
            created_by=self.user,
            modified_by=self.user,
        )

        super().setUp()

        self.channel_obj = Channel.create(
            self.project.org,
            self.user,
            None,
            "WWC",
            "Test WWC",
            "test",
            {"fake_key": "fake_value"},
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
            username="testuseradmin",
            password="123",
            email="test@weni.ai",
            is_superuser=True,
        )
        self.user = User.objects.create_user(username="fake@weni.ai", password="123", email="fake@weni.ai")
        self.projects = [
            Project.objects.create(
                name=f"Org {project}",
                timezone="America/Sao_Paulo",
                created_by=self.user,
                modified_by=self.user,
            )
            for project in range(2)
        ]

        for channel in range(6):
            Channel.create(
                self.projects[0] if channel % 2 == 0 else self.projects[1],
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
        org_uuid = str(self.projects[0].project_uuid)

        response = self.request_get(org=org_uuid).json()

        self.assertEqual(len(response), 3)

        channel = Channel.objects.get(uuid=response[0].get("uuid"))

        self.assertEqual(channel.org, self.projects[0].org)

    def get_url_namespace(self):
        return "channel-list"


class ListChannelAvailableTestCase(TembaTest, TembaRequestMixin):
    url = "/api/v2/flows-backend/channels/"

    def setUp(self):
        super().setUp()
        content_type = ContentType.objects.get_for_model(User)
        self.user = User.objects.create_user(username="fake@weni.ai", password="123", email="fake@weni.ai")
        self.admin.user_permissions.create(codename="can_communicate_internally", content_type=content_type)

    def test_list_all_channels(self):
        factory = APIRequestFactory()
        view = AvailableChannels.as_view({"get": "list"})
        view.permission_classes = []

        request = factory.get(self.url)
        force_authenticate(request, user=self.admin)
        response = view(request)
        total_attrs = 0

        channel_types = response.data.get("channel_types")
        for key in channel_types.keys():
            attributes = response.data.get("channel_types").get(key)
            if attributes:
                if len(attributes) > 0:
                    total_attrs += 1

        # checks if status code is 200 - ok
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # checks if the amount of #types returned is equivalent to the available response types
        self.assertEqual(len(TYPES), len(response.data.get("channel_types")))
        # checks if response data have existing attributes
        self.assertEqual(total_attrs, len(TYPES))

    def test_list_channels_without_authentication(self):
        """testing without authenticated user"""
        factory = APIRequestFactory()
        view = AvailableChannels.as_view({"get": "list"})

        request = factory.get(self.url)
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_channels_without_permission(self):
        """testing user without permission"""
        factory = APIRequestFactory()
        view = AvailableChannels.as_view({"get": "list"})

        request = factory.get(self.url)
        force_authenticate(request, user=self.user)
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_channel_with_permission(self):
        """Testing retrieve response is ok"""
        have_attribute = False
        have_form = False
        form_ok = True

        factory = APIRequestFactory()
        request = factory.get(self.url)
        view = AvailableChannels.as_view({"get": "retrieve"})
        view.permission_classes = []
        force_authenticate(request, user=self.admin)
        response = view(request, "ac")

        if response.data.get("attributes"):
            have_attribute = True

        if response.data.get("form"):
            have_form = True
            if len(response.data.get("form")) > 0:
                form = response.data.get("form")
                for field in form:
                    if not field.get("name") or not field.get("type") or not field.get("help_text"):
                        form_ok = False

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(True, have_attribute)
        if have_form:
            self.assertEqual(True, form_ok)

    def test_retrieve_channel_without_permission(self):
        """testing retrieve without permission"""
        factory = APIRequestFactory()
        view = AvailableChannels.as_view({"get": "retrieve"})

        request = factory.get(self.url)
        force_authenticate(request, user=self.user)
        response = view(request, "ac")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_channel_without_authentication(self):
        """testing retrieve without being authenticated"""
        factory = APIRequestFactory()
        view = AvailableChannels.as_view({"get": "retrieve"})

        request = factory.get(self.url)
        response = view(request, "ac")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def get_url_namespace(self):
        return "api.v2.flows_backend.channels-list"

    '''def test_invalid_response_info_form(self):
        """test missing values"""
        self.assertEqual(extract_form_info("", "name_field"), None)

    def test_invalid_response_info_type(self):
        """test missing values"""
        self.assertEqual(extract_type_info(""), None)'''


'''class FormatFunctionTestCase(TestCase):
    types = TYPES

    def test_form_with_values(self):
        """ checks if the treatment was done correctly """
        test_form = {
            'widget': to_object(**{'input_type': 'text'}),
            'help_text': 'test field',
            'label': 'test_label'
        }

        expect_form = {
            'name': 'test_form01',
            'type': 'text',
            'help_text': 'test field'
        }

        result = extract_form_info(to_object(**test_form),'test_form01')
        self.assertEqual(result, expect_form)

    def test_form_without_name_value(self):
        """ check response without #name attribute """
        test_form = {
            'widget': to_object(**{'input_type': 'text'}),
            'help_text': 'test field',
            'label': 'test_label'
        }
        result = extract_form_info(to_object(**test_form),'')
        self.assertEqual(result, None)

    def test_form_without_type_value(self):
        """ check response without #widget attribute """
        test_form = {
            'help_text': 'test field',
            'label': 'test_label'
        }
        result = extract_form_info(to_object(**test_form),'test_form03')
        self.assertEqual(result, None)

    def test_type_contains_code_and_name(self):
        """ make sure that all results have code and name """
        have_code_name = True
        for value in self.types:
            type_in = self.types[value]
            result = extract_type_info(type_in)
            if not (result.get('code')) or not (result.get('name')):
                have_code_name = False

        self.assertEqual(have_code_name, True)

    def test_all_types_response_contains_dict(self):
        """ make sure that all results have been processed and converted to dictionaries """
        for value in self.types:
            type_in = self.types[value]
            result = extract_type_info(type_in)
            self.assertEqual(type(result), dict)


class to_object:
    def __init__(self, **entries):
        return self.__dict__.update(entries)
'''
