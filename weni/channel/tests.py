from abc import ABC, abstractmethod
from uuid import uuid1

from django.contrib.auth.models import Group
from django.urls import reverse
from django.utils import timezone as tz
from django.utils.http import urlencode
from django.contrib.auth.models import User

from temba.api.models import APIToken

from temba.flows.models import Flow
from temba.orgs.models import Org
from temba.contacts.models import Contact

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

        return self.client.get(url, HTTP_AUTHORIZATION=f"Token {token.key}")

    def request_post(self, **data):
        url = reverse(self.get_url_namespace())
        token = APIToken.get_or_create(self.org, self.admin, Group.objects.get(name="Administrators"))

        return self.client.post(url, HTTP_AUTHORIZATION=f"Token {token.key}", json=data)

    @abstractmethod
    def get_url_namespace(self):
        ...

class ChannelTestCase(TembaTest, TembaRequestMixin):
    
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="123", email="test@weni.ai")
        self.org = Org.objects.create(name="Temba", timezone="Africa/Kigali", created_by=self.user, modified_by=self.user)

        self.channel = self.create_channel(channel_type="WA", name="channel_test", address="address_test", org=self.org)

        super().setUp()

    def test_list(self):
        channel_request = self.request_get()

        self.assertEqual(channel_request.data['results'][0]['name'], self.channel.name)

    def test_create(self):
        payload = {
            "user": str(self.user.id),
            "org": str(self.org.uuid),
            "data": "",
            "channeltype_code": ""
        }
        create_request = self.request_post(json=payload)

        self.assertEqual(create_request.status_code, 200)

    def test_retrieve(self):
        channel_request = self.request_get(uuid=self.channel.uuid)

        self.assertEqual(channel_request.data['results'][0]['name'], self.channel.name)

    def get_url_namespace(self):
        return "api.v2.channel"