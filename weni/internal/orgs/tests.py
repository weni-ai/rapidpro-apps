import json
from abc import ABC, abstractmethod
from datetime import datetime
import random
from unittest.mock import patch

from django.contrib.auth.models import Group
from django.contrib.auth.models import User
from django.conf import settings
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

    def request_get(self, **query_params):
        url = self.reverse(self.get_url_namespace(), query_params=query_params)
        url = url.replace("channel", "channel.json")
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

    def request_delete(self, uuid, **query_params):
        url = self.reverse(self.get_url_namespace(), kwargs={"uuid": uuid}, query_params=query_params)
        token = APIToken.get_or_create(self.org, self.admin, Group.objects.get(name="Administrators"))

        return self.client.delete(f"{url}", HTTP_AUTHORIZATION=f"Token {token.key}")

    def request_patch(self, uuid, data):
        url = self.reverse(self.get_url_namespace(), kwargs={"uuid": uuid})
        token = APIToken.get_or_create(self.org, self.admin, Group.objects.get(name="Administrators"))

        return self.client.patch(
            url, HTTP_AUTHORIZATION=f"Token {token.key}", data=json.dumps(data), content_type="application/json"
        )

    @abstractmethod
    def get_url_namespace(self):
        ...


class OrgListTest(TembaTest, TembaRequestMixin):

    WRONG_ID = -1
    WRONG_UUID = "31313-dasda-dasdasd-23123"
    WRONG_EMAIL = "wrong@email.com"

    def setUp(self):
        User.objects.create_user(username="testuser", password="123", email="test@weni.ai")
        User.objects.create_user(username="weniuser", password="123", email="wene@user.com")

        user = User.objects.get(username="testuser")

        Org.objects.create(name="Tembinha", timezone="Africa/Kigali", created_by=user, modified_by=user)
        Org.objects.create(name="Weni", timezone="Africa/Kigali", created_by=user, modified_by=user)
        Org.objects.create(name="Test", timezone="Africa/Kigali", created_by=user, modified_by=user)

        super().setUp()

    def test_list_orgs(self):
        response = self.request_get()
        self.assertEqual(response.status_code, 400)

        response = self.request_get(user_email="wrong@email.com")
        self.assertEqual(response.status_code, 404)

        orgs = Org.objects.all()
        user = User.objects.get(username="testuser")

        weni_org = orgs.get(name="Weni")
        temba_org = orgs.get(name="Tembinha")
        test_org = orgs.get(name="Test")

        weni_org.administrators.add(user)
        weni_org.is_active = False
        weni_org.save(update_fields=["is_active"])

        response = self.request_get(user_email=user.email).json()
        self.assertEquals(len(response), 0)

        weni_org.is_active = True
        weni_org.save(update_fields=["is_active"])

        response = self.request_get(user_email=user.email).json()
        self.assertEquals(len(response), 1)

        temba_org.viewers.add(user)
        response = self.request_get(user_email=user.email).json()
        self.assertEquals(len(response), 2)

        test_org.editors.add(user)
        response = self.request_get(user_email=user.email).json()
        self.assertEquals(len(response), 3)

    def test_list_users_on_org(self):
        org = Org.objects.get(name="Tembinha")

        testuser = User.objects.get(username="testuser")
        weniuser = User.objects.get(username="weniuser")

        org.administrators.add(testuser)
        response = self.request_get(user_email=testuser.email).json()
        self.assertEquals(len(response[0].get("users")), 1)

        org.administrators.add(weniuser)
        response = self.request_get(user_email=testuser.email).json()
        self.assertEquals(len(response[0].get("users")), 2)

    def get_url_namespace(self):
        return "orgs-list"


class OrgCreateTest(TembaTest, TembaRequestMixin):

    WRONG_ID = -1
    WRONG_UUID = "31313-dasda-dasdasd-23123"
    WRONG_EMAIL = "wrong@email.com"

    def setUp(self):

        User.objects.create_user(username="testuser", password="123", email="test@weni.ai")
        User.objects.create_user(username="weniuser", password="123", email="wene@user.com")

        user = User.objects.get(username="testuser")

        Org.objects.create(name="Tembinha", timezone="Africa/Kigali", created_by=user, modified_by=user)
        Org.objects.create(name="Weni", timezone="Africa/Kigali", created_by=user, modified_by=user)
        Org.objects.create(name="Test", timezone="Africa/Kigali", created_by=user, modified_by=user)

        super().setUp()

    @patch("temba.orgs.models.Org.create_sample_flows")
    def test_create_org(self, mock):

        org_name = "TestCreateOrg"
        user = User.objects.first()

        response = self.request_post(data=dict(name=org_name, timezone="Wrong/Zone", user_email=user.email)).json()

        self.assertEqual(response.get("timezone")[0], '"Wrong/Zone" is not a valid choice.')

        response = self.request_post(
            data=dict(name=org_name, timezone="Africa/Kigali", user_email="newemail@email.com")
        ).json()

        newuser_qs = User.objects.filter(email="newemail@email.com")

        self.assertTrue(newuser_qs.exists())

        newuser = newuser_qs.first()

        orgs = Org.objects.filter(name=org_name)
        org = orgs.first()

        self.assertEquals(orgs.count(), 1)

        created_by = org.created_by
        modified_by = org.modified_by
        administrators = org.administrators.all()
        administrator = administrators.get(pk=newuser.pk)

        self.assertEquals(created_by, newuser)
        self.assertEquals(modified_by, newuser)
        self.assertFalse(org.uses_topups)

        self.assertEquals(administrators.count(), 1)
        self.assertEquals(administrator, newuser)

        response = self.request_post(
            data=dict(name="neworg", timezone="Africa/Kigali", user_email="newemail@email.com")
        ).json()

        self.assertEqual(User.objects.filter(email="newemail@email.com").count(), 1)

    def get_url_namespace(self):
        return "orgs-list"


class OrgRetrieveTest(TembaTest, TembaRequestMixin):

    WRONG_ID = -1
    WRONG_UUID = "31313-dasda-dasdasd-23123"
    WRONG_EMAIL = "wrong@email.com"

    def setUp(self):

        User.objects.create_user(username="testuser", password="123", email="test@weni.ai")
        User.objects.create_user(username="weniuser", password="123", email="wene@user.com")

        user = User.objects.get(username="testuser")

        Org.objects.create(name="Tembinha", timezone="Africa/Kigali", created_by=user, modified_by=user)
        Org.objects.create(name="Weni", timezone="Africa/Kigali", created_by=user, modified_by=user)
        Org.objects.create(name="Test", timezone="Africa/Kigali", created_by=user, modified_by=user)

        super().setUp()

    def test_retrieve_org(self):
        org = Org.objects.last()
        user = User.objects.last()

        permission_types = ("administrator", "viewer", "editor", "surveyor")

        random_permission = random.choice(permission_types)

        if random_permission == "administrator":
            org.administrators.add(user)
        if random_permission == "viewer":
            org.viewers.add(user)
        if random_permission == "editor":
            org.editors.add(user)
        if random_permission == "surveyor":
            org.surveyors.add(user)

        org_uuid = str(org.uuid)
        org_timezone = str(org.timezone)

        response = self.request_detail(uuid=org_uuid).json()

        response_user = response.get("users")[-1]

        self.assertEqual(response.get("id"), org.id)
        self.assertEqual(response.get("name"), org.name)
        self.assertEqual(response.get("uuid"), org_uuid)
        self.assertEqual(org_timezone, response.get("timezone"))
        self.assertEqual(org.date_format, response.get("date_format"))

        self.assertEqual(user.id, response_user.get("id"))
        self.assertEqual(user.email, response_user.get("email"))
        self.assertEqual(user.username, response_user.get("username"))

        self.assertEqual(response_user.get("permission_type"), random_permission)

    def get_url_namespace(self):
        return "orgs-detail"


class OrgDestroyTest(TembaTest, TembaRequestMixin):

    WRONG_ID = -1
    WRONG_UUID = "31313-dasda-dasdasd-23123"
    WRONG_EMAIL = "wrong@email.com"

    def setUp(self):

        User.objects.create_user(username="testuser", password="123", email="test@weni.ai")
        User.objects.create_user(username="weniuser", password="123", email="wene@user.com")

        user = User.objects.get(username="testuser")

        Org.objects.create(name="Tembinha", timezone="Africa/Kigali", created_by=user, modified_by=user)
        Org.objects.create(name="Weni", timezone="Africa/Kigali", created_by=user, modified_by=user)
        Org.objects.create(name="Test", timezone="Africa/Kigali", created_by=user, modified_by=user)

        super().setUp()

    def test_destroy_org(self):
        org = Org.objects.last()
        is_active = org.is_active
        modified_by = org.modified_by

        weniuser = User.objects.get(username="weniuser")

        self.request_delete(uuid=str(org.uuid), user_email=weniuser.email)

        destroyed_org = Org.objects.get(id=org.id)

        self.assertFalse(destroyed_org.is_active)
        self.assertNotEquals(is_active, destroyed_org.is_active)
        self.assertEquals(weniuser, destroyed_org.modified_by)
        self.assertNotEquals(modified_by, destroyed_org.modified_by)

    def get_url_namespace(self):
        return "orgs-detail"


class OrgUpdateTest(TembaTest, TembaRequestMixin):

    WRONG_ID = -1
    WRONG_UUID = "31313-dasda-dasdasd-23123"
    WRONG_EMAIL = "wrong@email.com"

    def setUp(self):

        User.objects.create_user(username="testuser", password="123", email="test@weni.ai")
        User.objects.create_user(username="weniuser", password="123", email="wene@user.com")

        user = User.objects.get(username="testuser")

        Org.objects.create(name="Tembinha", timezone="Africa/Kigali", created_by=user, modified_by=user)
        Org.objects.create(name="Weni", timezone="Africa/Kigali", created_by=user, modified_by=user)
        Org.objects.create(name="Test", timezone="Africa/Kigali", created_by=user, modified_by=user)

        super().setUp()

    def test_update_org(self):
        org = Org.objects.first()

        permission_error_message = f"User: {self.user.id} has no permission to update Org: {org.uuid}"

        response = self.request_patch(uuid=str(org.uuid), data=dict(modified_by=self.user.email)).json()

        self.assertEqual(response[0], permission_error_message)

        self.user.is_superuser = True
        self.user.save()

        org.administrators.add(self.user)

        update_fields = {
            "name": "NewOrgName",
            "timezone": "America/Maceio",
            "date_format": "M",
            "plan": settings.INFINITY_PLAN,
            "plan_end": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "brand": "push.ia",
            "is_anon": True,
            "is_multi_user": True,
            "is_multi_org": True,
            "is_suspended": True,
            "modified_by": self.user.email,
        }

        response = self.request_patch(uuid=str(org.uuid), data=update_fields).json()

        updated_org = Org.objects.get(pk=org.pk)

        self.assertEquals(update_fields.get("name"), updated_org.name)
        self.assertNotEquals(org.name, updated_org.name)

        self.assertEquals(update_fields.get("timezone"), str(updated_org.timezone))
        self.assertNotEquals(org.timezone, updated_org.timezone)

        self.assertEquals(update_fields.get("date_format"), updated_org.date_format)
        self.assertNotEquals(org.date_format, updated_org.date_format)

        self.assertEquals(updated_org.plan, settings.INFINITY_PLAN)
        self.assertNotEquals(org.plan, updated_org.plan)
        self.assertFalse(updated_org.uses_topups)
        self.assertEquals(updated_org.plan_end, None)

        self.assertEquals(update_fields.get("brand"), updated_org.brand)
        self.assertNotEquals(org.brand, updated_org.brand)

        self.assertEquals(update_fields.get("is_anon"), updated_org.is_anon)
        self.assertNotEquals(org.is_anon, updated_org.is_anon)

        self.assertEquals(update_fields.get("is_multi_user"), updated_org.is_multi_user)
        self.assertNotEquals(org.is_multi_user, updated_org.is_multi_user)

        self.assertEquals(update_fields.get("is_multi_org"), updated_org.is_multi_org)
        self.assertNotEquals(org.is_multi_org, updated_org.is_multi_org)

        self.assertEquals(update_fields.get("is_suspended"), updated_org.is_suspended)
        self.assertNotEquals(org.is_suspended, updated_org.is_suspended)

    def get_url_namespace(self):
        return "orgs-detail"
