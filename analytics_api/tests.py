from uuid import uuid1

from django.contrib.auth.models import Group
from django.urls import reverse
from django.utils.http import urlencode

from temba.api.models import APIToken
from temba.contacts.models import Contact
from temba.tests import TembaTest, mock_mailroom


class AnalyticsContactTest(TembaTest):
    @mock_mailroom
    def setUp(self, mr_mocks):
        super().setUp()

        # create some static groups
        self.group = self.create_group("Customers", org=self.org)
        self.group2 = self.create_group("Nerds", org=self.org)

        # create some contacts
        for x in range(0, 10):
            contact_name = "Joe Blow " + str(x)
            created_contact = self.create_contact(contact_name)
            self.group2.contacts.add(created_contact)

        # create a contact without group
        self.create_contact("Contact without group")

        # create blocked contacts
        for x in range(0, 5):
            contact_name = "Joe Blocked " + str(x)
            blocked_contact = self.create_contact(contact_name)
            blocked_contact.block(self.user)

        # create stopped contacts
        for x in range(0, 5):
            contact_name = "Joe stopped " + str(x)
            blocked_contact = self.create_contact(contact_name)
            blocked_contact.stop(self.user)

        # create archived contacts
        for x in range(0, 5):
            contact_name = "Joe archived " + str(x)
            blocked_contact = self.create_contact(contact_name)
            blocked_contact.archive(self.user)

        # create deleted contacts
        for x in range(0, 3):
            self.create_contact("Joe deleted {}".format(x)).release(self.user)

    def reverse(self, viewname, kwargs=None, query_params=None):
        url = reverse(viewname, kwargs=kwargs)

        if query_params:
            return "%s?%s" % (url, urlencode(query_params))
        else:
            return url

    def get_response(self, **query_params):
        url = self.reverse("api.v2.analytics.contacts", query_params=query_params)
        token = APIToken.get_or_create(self.org, self.admin, Group.objects.get(name="Administrators"))

        return self.client.get(url, HTTP_AUTHORIZATION=f"Token {token.key}")

    def test_total_contacts(self):
        response = self.get_response()
        self.assertEqual(response.json().get("total"), 26)

    def test_contacts_by_status(self):
        response = self.get_response()
        self.assertEqual(response.json().get("current").get("actives"), 11)
        self.assertEqual(response.json().get("current").get("blocked"), 5)
        self.assertEqual(response.json().get("current").get("stopped"), 5)
        self.assertEqual(response.json().get("current").get("archived"), 5)

    def test_by_date(self):
        response = self.get_response()
        last_created_on = Contact.objects.values_list("created_on__date", flat=True).last().strftime("%Y-%m-%d")
        contacts = response.json().get("by_date").get(last_created_on)
        self.assertEqual(contacts, 26)

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