from django.contrib.auth.models import Group
from django.urls import reverse

from temba.api.models import APIToken
from temba.tests import TembaTest
from temba.contacts.models import Contact
from django.utils.http import urlencode


class AnalyticsContactTest(TembaTest):
    def setUp(self):
        super().setUp()

        for x in range(0, 10):
            contact_name = "Joe Blow " + str(x)
            self.create_contact(contact_name)

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

        self.assertEqual(response.json().get("total"), Contact.objects.count())

    def test_active_contacts(self):
        response = self.get_response()

        self.assertEqual(response.json().get("current").get("actives"), Contact.objects.filter(status="A").count())

    def test_by_date(self):
        response = self.get_response()

        last_created_on = Contact.objects.values_list('created_on__date', flat=True).last().strftime('%Y-%m-%d')
        contacts = response.json().get("by_date").get(last_created_on)

        self.assertEqual(contacts, Contact.objects.filter(status="A").count())
