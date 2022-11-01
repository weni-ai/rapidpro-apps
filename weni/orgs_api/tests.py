import json
from random import randint
from abc import ABC, abstractmethod

from django.contrib.auth.models import Group
from django.contrib.auth.models import User
from django.utils.http import urlencode
from django.urls import reverse

from temba.orgs.models import Org

from temba.api.models import APIToken
from temba.tests import TembaTest


class TembaRequestMixin(ABC):
    def reverse(self, viewname, kwargs=None, query_params=None):
        url = reverse(viewname, kwargs=kwargs)

        if query_params:
            return "%s?%s" % (url, urlencode(query_params))
        else:
            return url

    def request_patch(self, uuid, data):
        url = self.reverse(self.get_url_namespace(), kwargs={"uuid": uuid})
        token = APIToken.get_or_create(self.org, self.admin, Group.objects.get(name="Administrators"))

        return self.client.patch(
            url, HTTP_AUTHORIZATION=f"Token {token.key}", data=json.dumps(data), content_type="application/json"
        )

    @abstractmethod
    def get_url_namespace(self):
        ...


class SuspendOrgTest(TembaTest, TembaRequestMixin):
    def setUp(self):
        User.objects.create_user(username="testuser", password="123", email="test@weni.ai")

        user = User.objects.get(username="testuser")

        Org.objects.create(name="Tembinha", timezone="Africa/Kigali", created_by=user, modified_by=user)

        super().setUp()

    def test_block_org_without_config(self):
        org = Org.objects.get(name="Tembinha")

        is_suspended = bool(randint(0, 1))

        self.request_patch(uuid=org.uuid, data={"is_suspended": is_suspended})

        self.assertEqual(org.config, {})

        org = Org.objects.get(name="Tembinha")

        self.assertEqual(org.config.get("is_suspended"), is_suspended)

    def test_block_org_with_config(self):
        org = Org.objects.get(name="Tembinha")
        org.config["another_key"] = "test"
        org.save()

        is_suspended = bool(randint(0, 1))

        self.request_patch(uuid=org.uuid, data={"is_suspended": is_suspended})

        org = Org.objects.get(name="Tembinha")
        self.assertEqual(org.config.get("is_suspended"), is_suspended)
        self.assertEqual(org.config.get("another_key"), "test")

    def get_url_namespace(self):
        return "org-is-suspended"
