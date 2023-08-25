import json
from abc import ABC, abstractmethod
from unittest.mock import patch
from django.contrib.auth.models import User

from django.contrib.auth.models import Group
from django.urls import reverse
from django.utils.http import urlencode

from temba.api.models import APIToken

from temba.tests import TembaTest
from temba.orgs.models import Org
from temba.classifiers.models import Classifier, Intent
from temba.classifiers.types.wit import WitType
from temba.classifiers.types.luis import LuisType


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
        # self.client.force_login(self.admin)
        return self.client.get(f"{url}", HTTP_AUTHORIZATION=f"Token {token.key}")

    def request_detail(self, uuid):
        url = self.reverse(self.get_url_namespace(), kwargs={"uuid": uuid})
        token = APIToken.get_or_create(self.org, self.admin, Group.objects.get(name="Administrators"))

        return self.client.get(f"{url}", HTTP_AUTHORIZATION=f"Token {token.key}")

    def request_post(self, data):
        url = reverse(self.get_url_namespace())
        token = APIToken.get_or_create(self.org, self.admin, Group.objects.get(name="Administrators"))

        return self.client.post(
            url,
            HTTP_AUTHORIZATION=f"Token {token.key}",
            data=json.dumps(data),
            content_type="application/json",
        )

    def request_delete(self, uuid, user_email):
        url = self.reverse(
            self.get_url_namespace(),
            query_params={"user_email": user_email},
            kwargs={"uuid": uuid},
        )
        token = APIToken.get_or_create(self.org, self.admin, Group.objects.get(name="Administrators"))

        return self.client.delete(f"{url}", HTTP_AUTHORIZATION=f"Token {token.key}")

    @abstractmethod
    def get_url_namespace(self):
        ...


class ClassifierTestCase(TembaTest, TembaRequestMixin):
    def setUp(self):
        self.config = {"access_token": "hbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"}

        self.admin = User.objects.create_user(
            username="testuser", password="123", email="test@weni.ai", is_superuser=True
        )

        print(self.admin.is_authenticated)

        self.org = Org.objects.create(
            name="Weni",
            timezone="America/Maceio",
            created_by=self.admin,
            modified_by=self.admin,
        )

        super().setUp()

    def test_list_classifier(self):
        org = Org.objects.first()
        org_uuid = str(org.uuid)

        classifier = Classifier.create(org, self.admin, WitType.slug, "Booker", self.config, sync=False)

        response = self.request_get(org_uuid=org_uuid, is_active=1).json()
        print(response)

        self.assertEqual(len(response), 1)

        response = response[0]

        self.assertEqual(response.get("name"), "Booker")
        self.assertEqual(response.get("classifier_type"), WitType.slug)
        self.assertEqual(response.get("uuid"), str(classifier.uuid))
        self.assertEqual(response.get("access_token"), self.config["access_token"])

        classifier = Classifier.create(org, self.admin, LuisType.slug, "Test", self.config, sync=False)

        response = self.request_get(org_uuid=org_uuid, is_active=1).json()

        self.assertEqual(len(response), 2)

        response = response[1]

        self.assertEqual(response.get("name"), "Test")
        self.assertEqual(response.get("classifier_type"), LuisType.slug)
        self.assertEqual(response.get("uuid"), str(classifier.uuid))
        self.assertEqual(response.get("access_token"), self.config["access_token"])

        response = self.request_get(org_uuid=org_uuid, is_active=1, classifier_type=LuisType.slug).json()

        self.assertEqual(len(response), 1)

        response = response[0]

        self.assertEqual(response.get("name"), "Test")
        self.assertEqual(response.get("classifier_type"), LuisType.slug)
        self.assertEqual(response.get("uuid"), str(classifier.uuid))
        self.assertEqual(response.get("access_token"), self.config["access_token"])

        classifier = Classifier.create(org, self.admin, LuisType.slug, "Test2", self.config, sync=False)

        response = self.request_get(org_uuid=org_uuid, is_active=1, classifier_type=LuisType.slug).json()

        self.assertEqual(len(response), 2)

        response = self.request_get(org_uuid=org_uuid, is_active=1).json()

        self.assertEqual(len(response), 3)

    def get_url_namespace(self):
        return "classifier-list"


class ClassifierCreateTestCase(TembaTest, TembaRequestMixin):
    def setUp(self):
        self.config = {"access_token": "hbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"}

        self.admin = User.objects.create_user(
            username="testuser", password="123", email="test@weni.ai", is_superuser=True
        )

        self.org = Org.objects.create(
            name="Weni",
            timezone="America/Maceio",
            created_by=self.admin,
            modified_by=self.admin,
        )

        super().setUp()

    @patch("temba.classifiers.tasks.sync_classifier_intents")
    def test_create_classifier(self, mock):
        mock.return_value = None

        org = Org.objects.first()
        user = self.admin
        access_token = self.config["access_token"]

        name = "Test Name"
        classifier_type = "Test Type"

        payload = {
            "classifier_type": classifier_type,
            "user": user.email,
            "org": str(org.uuid),
            "name": name,
            "access_token": access_token,
        }

        response = self.request_post(data=payload).json()

        self.assertEqual(response.get("name"), name)
        self.assertEqual(response.get("classifier_type"), classifier_type)
        self.assertEqual(response.get("access_token"), access_token)

    def get_url_namespace(self):
        return "classifier-list"


class ClassifierRetrieveTestCase(TembaTest, TembaRequestMixin):
    def setUp(self):
        self.config = {"access_token": "hbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"}

        self.admin = User.objects.create_user(
            username="testuser", password="123", email="test@weni.ai", is_superuser=True
        )

        self.org = Org.objects.create(
            name="Weni",
            timezone="America/Maceio",
            created_by=self.admin,
            modified_by=self.admin,
        )

        super().setUp()

    def test_retrieve_classifier_by_valid_uuid(self):
        classifier = Classifier.create(self.org, self.admin, LuisType.slug, "Test2", self.config, sync=False)
        response = self.request_detail(uuid=str(classifier.uuid)).json()

        self.assertEqual(classifier.classifier_type, response.get("classifier_type"))
        self.assertEqual(classifier.name, response.get("name"))
        self.assertEqual(classifier.config["access_token"], response.get("access_token"))
        self.assertEqual(classifier.is_active, response.get("is_active"))

    def get_url_namespace(self):
        return "classifier-detail"


class ClassifierDestroyTestCase(TembaTest, TembaRequestMixin):
    def setUp(self):
        self.config = {"access_token": "hbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"}

        self.admin = User.objects.create_user(
            username="testuser", password="123", email="test@weni.ai", is_superuser=True
        )

        self.org = Org.objects.create(
            name="Weni",
            timezone="America/Maceio",
            created_by=self.admin,
            modified_by=self.admin,
        )

        super().setUp()

    def test_destroy_classifier_by_valid_uuid(self):
        classifier = Classifier.create(self.org, self.admin, LuisType.slug, "Test2", self.config, sync=False)
        Intent.objects.create(classifier=classifier, name="Test Intent", external_id="FakeExternal")

        self.assertEqual(classifier.intents.count(), 1)

        self.request_delete(uuid=str(classifier.uuid), user_email=self.admin.email)

        classifier = Classifier.objects.get(uuid=classifier.uuid)
        self.assertEqual(classifier.intents.count(), 0)
        self.assertFalse(classifier.is_active)

    def get_url_namespace(self):
        return "classifier-detail"
