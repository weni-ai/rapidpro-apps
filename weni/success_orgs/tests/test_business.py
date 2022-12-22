import uuid

from django.test import TestCase
from django.contrib.auth import get_user_model

from weni.success_orgs.business import (
    UserDoesNotExist,
    OrgDoesNotExist,
    get_user_by_email,
    get_user_success_orgs,
    retrieve_success_org,
)
from temba.orgs.models import Org
from temba.channels.models import Channel
from temba.classifiers.models import Classifier
from temba.flows.models import Flow


User = get_user_model()


class SetupMixin(object):
    def setUp(self) -> None:
        self.user_email = "fake@weni.ai"
        self.user = User.objects.create(email=self.user_email)
        self.org = Org.objects.create(created_by=self.user, modified_by=self.user, name="fakeorg")


class GetUserByEmailTestCase(SetupMixin, TestCase):
    def test_get_user_by_email(self):
        user = get_user_by_email(self.user_email)
        self.assertEqual(user.email, self.user_email)

    def test_get_user_by_email_raise_does_not_exist_exception_with_wrong_email(self):
        with self.assertRaises(UserDoesNotExist):
            get_user_by_email("wrong@weni.ai")


class GetUserSuccessOrgsTestCase(SetupMixin, TestCase):
    def test_function_returns_extra_fields(self):
        org = get_user_success_orgs(self.user).first()
        self.assertTrue(hasattr(org, "has_ia"))
        self.assertTrue(hasattr(org, "has_flows"))
        self.assertTrue(hasattr(org, "has_channel"))
        self.assertTrue(hasattr(org, "has_msg"))

    def test_when_adding_classifier_it_returns_true(self):
        Classifier.objects.create(
            org=self.org, created_by=self.user, modified_by=self.user, config={}, classifier_type="bothub"
        )

        org = get_user_success_orgs(self.user).first()
        self.assertTrue(org.has_ia)
        self.assertFalse(org.has_flows)
        self.assertFalse(org.has_channel)
        self.assertFalse(org.has_msg)

    def test_when_adding_flow_it_returns_true(self):
        Flow.objects.create(org=self.org, created_by=self.user, modified_by=self.user, saved_by=self.user)

        org = get_user_success_orgs(self.user).first()
        self.assertFalse(org.has_ia)
        self.assertTrue(org.has_flows)
        self.assertFalse(org.has_channel)
        self.assertFalse(org.has_msg)

    def test_when_adding_channel_it_returns_true(self):
        Channel.objects.create(org=self.org, created_by=self.user, modified_by=self.user)

        org = get_user_success_orgs(self.user).first()
        self.assertFalse(org.has_ia)
        self.assertFalse(org.has_flows)
        self.assertTrue(org.has_channel)
        self.assertFalse(org.has_msg)


class RetrieveSuccessOrgTestCase(SetupMixin, TestCase):
    def test_returns_org_by_uuid(self):
        org = retrieve_success_org(str(self.org.uuid))
        self.assertEqual(org, self.org)

    def test_retrieve_success_org_raise_does_not_exist_exception_with_wrong_uuid(self):
        with self.assertRaises(OrgDoesNotExist):
            retrieve_success_org(uuid.uuid4())
