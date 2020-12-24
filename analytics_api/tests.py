from django.contrib.auth.models import Group
from django.urls import reverse

from temba.api.models import APIToken
from temba.tests import TembaTest
from temba.contacts.models import Contact


class AnalyticsContactTest(TembaTest):
    def setUp(self):
        super().setUp()

        for x in range(0, 10):
            contact_name = "Joe Blow " + str(x)
            self.create_contact(contact_name)

    def get_response(self):
        url = reverse("api.v2.analytics.contacts")
        token = APIToken.get_or_create(self.org, self.admin, Group.objects.get(name="Administrators"))

        return self.client.get(url, HTTP_AUTHORIZATION=f"Token {token.key}")

    def test_total_contacts(self):
        response = self.get_response()

        self.assertEqual(response.json().get("total"), Contact.objects.count())

    def test_active_contacts(self):
        response = self.get_response()

        self.assertEqual(response.json().get("current").get("actives"), Contact.objects.filter(status="A").count())

    def test_by_date(self):
        response = self.get_response()

        last_created_on = Contact.objects.last().created_on.strftime("%Y-%m-%d")
        contacts = response.json().get("by_date").get(last_created_on)

        self.assertEqual(contacts, Contact.objects.filter(status="A").count())
