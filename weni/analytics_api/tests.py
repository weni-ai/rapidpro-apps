from abc import ABC, abstractmethod
from uuid import uuid1

from django.contrib.auth.models import Group
from django.urls import reverse
from django.utils import timezone as tz
from django.utils.http import urlencode

from temba.api.models import APIToken
from temba.flows.models import FlowRun
from temba.tests import TembaTest, mock_mailroom


def format_date(dt):
    return dt.strftime("%Y-%m-%d")


class TembaRequestMixin(ABC):
    def reverse(self, viewname, kwargs=None, query_params=None):
        url = reverse(viewname, kwargs=kwargs)

        if query_params:
            return "%s?%s" % (url, urlencode(query_params))
        else:
            return url

    def get_response(self, **query_params):
        url = self.reverse(self.get_url_namespace(), query_params=query_params)
        token = APIToken.get_or_create(self.org, self.admin, Group.objects.get(name="Administrators"))

        return self.client.get(url, HTTP_AUTHORIZATION=f"Token {token.key}")

    @abstractmethod
    def get_url_namespace(self):
        ...


class AnalyticsContactTest(TembaTest, TembaRequestMixin):
    @mock_mailroom
    def setUp(self, mr_mocks):
        super().setUp()

        # create some static groups
        self.group = self.create_group("Customers", org=self.org)
        self.group2 = self.create_group("Nerds", org=self.org)

        # create some contacts
        for contact in range(0, 10):
            contact_name = "Joe Blow " + str(contact)
            created_contact = self.create_contact(contact_name)
            self.group2.contacts.add(created_contact)

        # create a contact without group
        self.create_contact("Contact without group")

        # create blocked contacts
        for contact in range(0, 5):
            contact_name = "Joe Blocked " + str(contact)
            blocked_contact = self.create_contact(contact_name)
            blocked_contact.block(self.user)

        # create stopped contacts
        for contact in range(0, 5):
            contact_name = "Joe stopped " + str(contact)
            blocked_contact = self.create_contact(contact_name)
            blocked_contact.stop(self.user)

        # create archived contacts
        for contact in range(0, 5):
            contact_name = "Joe archived " + str(contact)
            blocked_contact = self.create_contact(contact_name)
            blocked_contact.archive(self.user)

        # create deleted contacts
        for contact in range(0, 3):
            self.create_contact("Joe deleted {}".format(contact)).release(self.user)

        # Adds some contacts with another creation dates
        old_joe = self.create_contact("Old Joe")
        old_joe.created_on = tz.now() - tz.timedelta(days=1)
        old_joe.save(update_fields=["created_on"])

        older_joe = self.create_contact("Older Joe")
        older_joe.created_on = tz.now() - tz.timedelta(days=7)
        older_joe.save(update_fields=["created_on"])

    def get_url_namespace(self):
        return "api.v2.analytics.contacts"

    def test_total_contacts(self):
        response = self.get_response()
        self.assertEqual(response.json().get("total"), 28)

    def test_contacts_by_status(self):
        response = self.get_response()
        self.assertEqual(response.json().get("current").get("actives"), 13)
        self.assertEqual(response.json().get("current").get("blocked"), 5)
        self.assertEqual(response.json().get("current").get("stopped"), 5)
        self.assertEqual(response.json().get("current").get("archived"), 5)

    def test_by_date(self):
        response = self.get_response()
        contacts = response.json()["by_date"]

        today = format_date(tz.now())
        yesterday = format_date(tz.now() - tz.timedelta(1))
        last_week = format_date(tz.now() - tz.timedelta(7))

        self.assertEqual(contacts[today], 26)
        self.assertEqual(contacts[yesterday], 1)
        self.assertEqual(contacts[last_week], 1)

    def test_group_filter(self):
        response = self.get_response(group=self.group2.uuid)
        self.assertEqual(response.json().get("total"), 10)

    def test_non_existent_group_filter(self):
        random_uuid = uuid1()
        response = self.get_response(group=random_uuid)
        self.assertEqual(response.json().get("total"), 0)

    def test_deleted_contacts(self):
        response = self.get_response(deleted=True)
        self.assertEqual(response.json().get("total"), 3)

    def test_after_and_before(self):
        response = self.get_response()
        self.assertEqual(response.json().get("total"), 28)
        self.assertEqual(response.json().get("current").get("actives"), 13)
        self.assertEqual(response.json().get("current").get("blocked"), 5)
        self.assertEqual(response.json().get("current").get("stopped"), 5)
        self.assertEqual(response.json().get("current").get("archived"), 5)

        response = self.get_response(after=format_date(tz.now()))
        self.assertEqual(response.json().get("total"), 26)
        self.assertEqual(response.json().get("current").get("actives"), 11)
        self.assertEqual(response.json().get("current").get("blocked"), 5)
        self.assertEqual(response.json().get("current").get("stopped"), 5)
        self.assertEqual(response.json().get("current").get("archived"), 5)

        response = self.get_response(before=format_date(tz.now()))
        self.assertEqual(response.json().get("total"), 2)
        self.assertEqual(response.json().get("current").get("actives"), 2)
        self.assertEqual(response.json().get("current").get("blocked"), 0)
        self.assertEqual(response.json().get("current").get("stopped"), 0)
        self.assertEqual(response.json().get("current").get("archived"), 0)

        response = self.get_response(before=format_date(tz.now() - tz.timedelta(1)))
        self.assertEqual(response.json().get("total"), 1)
        self.assertEqual(response.json().get("current").get("actives"), 1)
        self.assertEqual(response.json().get("current").get("blocked"), 0)
        self.assertEqual(response.json().get("current").get("stopped"), 0)
        self.assertEqual(response.json().get("current").get("archived"), 0)

        response = self.get_response(before=format_date(tz.now() - tz.timedelta(7)))
        self.assertEqual(response.json().get("total"), 0)
        self.assertEqual(response.json().get("current").get("actives"), 0)
        self.assertEqual(response.json().get("current").get("blocked"), 0)
        self.assertEqual(response.json().get("current").get("stopped"), 0)
        self.assertEqual(response.json().get("current").get("archived"), 0)


class AnalyticsFlowRunTest(TembaTest, TembaRequestMixin):
    def setUp(self):
        super().setUp()

        self.flow = self.create_flow(name="flow_1")
        self.contact = self.create_contact(name="contact_1")

        self.flow_run_completed = FlowRun.objects.create(
            org=self.org, flow=self.flow, contact=self.contact, status=FlowRun.STATUS_COMPLETED
        )
        self.flow_run_waiting = FlowRun.objects.create(
            org=self.org, flow=self.flow, contact=self.contact, status=FlowRun.STATUS_WAITING
        )
        self.flow_run_active = FlowRun.objects.create(
            org=self.org, flow=self.flow, contact=self.contact, status=FlowRun.STATUS_ACTIVE
        )
        self.flow_run_interrupted = FlowRun.objects.create(
            org=self.org, flow=self.flow, contact=self.contact, status=FlowRun.STATUS_INTERRUPTED
        )
        self.flow_run_expired = FlowRun.objects.create(
            org=self.org, flow=self.flow, contact=self.contact, status=FlowRun.STATUS_EXPIRED
        )
        self.flow_run_failed = FlowRun.objects.create(
            org=self.org, flow=self.flow, contact=self.contact, status=FlowRun.STATUS_FAILED
        )

        self.flow_run_active.created_on = tz.now() - tz.timedelta(days=7)
        self.flow_run_active.save(update_fields=["created_on"])

        self.flow_run_interrupted.created_on = tz.now() - tz.timedelta(days=3)
        self.flow_run_interrupted.save(update_fields=["created_on"])

    def get_url_namespace(self):
        return "api.v2.analytics.flow_runs"

    def test_return_is_a_dict(self):
        response = self.get_response()
        self.assertIsInstance(response.json(), dict)

    def test_flow_name_as_key(self):
        response = self.get_response()
        self.assertEqual(list(response.json().keys())[0], "flow_1")
        self.assertIsNone(response.json().get("non_existent_flow", None))

    def test_uuid_is_returned(self):
        response = self.get_response()
        self.assertEqual(response.json().get(self.flow.name).get("uuid"), self.flow.uuid)

    def test_has_stats(self):
        response = self.get_response()
        self.assertIsNotNone(response.json().get(self.flow.name).get("stats", None))

    def test_stats_is_a_dict(self):
        response = self.get_response()
        self.assertIsInstance(response.json().get(self.flow.name).get("stats"), dict)

    def test_total(self):
        response = self.get_response()
        self.assertEqual(response.json().get(self.flow.name).get("stats").get("total"), 6)

    def test_by_status(self):
        response = self.get_response()
        by_status = response.json().get(self.flow.name).get("stats").get("by_status")
        self.assertEqual(by_status.get("active"), 1)
        self.assertEqual(by_status.get("waiting"), 1)
        self.assertEqual(by_status.get("completed"), 1)
        self.assertEqual(by_status.get("interrupted"), 1)
        self.assertEqual(by_status.get("expired"), 1)
        self.assertEqual(by_status.get("failed"), 1)

    def test_filter_after_and_before(self):
        response = self.get_response(after=format_date(tz.now()))
        self.assertEqual(response.json().get(self.flow.name).get("stats").get("total"), 4)
        self.assertEqual(response.json().get(self.flow.name).get("stats").get("by_status").get("active"), 0)
        self.assertEqual(response.json().get(self.flow.name).get("stats").get("by_status").get("interrupted"), 0)
        self.assertEqual(response.json().get(self.flow.name).get("stats").get("by_status").get("waiting"), 1)
        self.assertEqual(response.json().get(self.flow.name).get("stats").get("by_status").get("completed"), 1)
        self.assertEqual(response.json().get(self.flow.name).get("stats").get("by_status").get("expired"), 1)
        self.assertEqual(response.json().get(self.flow.name).get("stats").get("by_status").get("failed"), 1)

        response = self.get_response(before=format_date(tz.now()))
        self.assertEqual(response.json().get(self.flow.name).get("stats").get("total"), 2)
        self.assertEqual(response.json().get(self.flow.name).get("stats").get("by_status").get("active"), 1)
        self.assertEqual(response.json().get(self.flow.name).get("stats").get("by_status").get("interrupted"), 1)
        self.assertEqual(response.json().get(self.flow.name).get("stats").get("by_status").get("waiting"), 0)
        self.assertEqual(response.json().get(self.flow.name).get("stats").get("by_status").get("completed"), 0)
        self.assertEqual(response.json().get(self.flow.name).get("stats").get("by_status").get("expired"), 0)
        self.assertEqual(response.json().get(self.flow.name).get("stats").get("by_status").get("failed"), 0)

        response = self.get_response(
            after=format_date(tz.now() - tz.timedelta(3)), before=format_date(tz.now() - tz.timedelta(2))
        )
        self.assertEqual(response.json().get(self.flow.name).get("stats").get("total"), 1)
        self.assertEqual(response.json().get(self.flow.name).get("stats").get("by_status").get("active"), 0)
        self.assertEqual(response.json().get(self.flow.name).get("stats").get("by_status").get("interrupted"), 1)
        self.assertEqual(response.json().get(self.flow.name).get("stats").get("by_status").get("waiting"), 0)
        self.assertEqual(response.json().get(self.flow.name).get("stats").get("by_status").get("completed"), 0)
        self.assertEqual(response.json().get(self.flow.name).get("stats").get("by_status").get("expired"), 0)
        self.assertEqual(response.json().get(self.flow.name).get("stats").get("by_status").get("failed"), 0)

        response = self.get_response(
            after=format_date(tz.now() - tz.timedelta(7)), before=format_date(tz.now() - tz.timedelta(6))
        )
        self.assertEqual(response.json().get(self.flow.name).get("stats").get("total"), 1)
        self.assertEqual(response.json().get(self.flow.name).get("stats").get("by_status").get("active"), 1)
        self.assertEqual(response.json().get(self.flow.name).get("stats").get("by_status").get("interrupted"), 0)
        self.assertEqual(response.json().get(self.flow.name).get("stats").get("by_status").get("waiting"), 0)
        self.assertEqual(response.json().get(self.flow.name).get("stats").get("by_status").get("completed"), 0)
        self.assertEqual(response.json().get(self.flow.name).get("stats").get("by_status").get("expired"), 0)
        self.assertEqual(response.json().get(self.flow.name).get("stats").get("by_status").get("failed"), 0)

    def test_filter_by_flow_uuid(self):
        response = self.get_response(flow_uuid=self.flow.uuid)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(list(response.json().keys())[0], "flow_1")
        response = self.get_response(flow_uuid="00000000-0000-0000-0000-000000000000")  # fake uuid
        self.assertEqual(response.json(), {})
