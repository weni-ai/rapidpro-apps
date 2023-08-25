from abc import ABC, abstractmethod

from django.contrib.auth.models import Group
from django.urls import reverse
from django.utils.http import urlencode
from django.contrib.auth.models import User

from temba.api.models import APIToken
from temba.flows.models import Flow
from temba.tests import TembaTest
from weni.internal.models import Project
from weni.internal.statistic.views import StatisticEndpoint


view = StatisticEndpoint
view.permission_classes = []


class TembaRequestMixin(ABC):
    def reverse(self, viewname, kwargs=None, query_params=None):
        url = reverse(viewname, kwargs=kwargs)

        if query_params:
            return "%s?%s" % (url, urlencode(query_params))

        return url

    def request_detail(self, uuid):
        url = self.reverse(self.get_url_namespace(), kwargs={"project_uuid": uuid})
        token = APIToken.get_or_create(self.org, self.admin, Group.objects.get(name="Administrators"))

        return self.client.get(f"{url}", HTTP_AUTHORIZATION=f"Token {token.key}")

    @abstractmethod
    def get_url_namespace(self):
        ...


class StatisticTestCase(TembaTest, TembaRequestMixin):
    def setUp(self):
        super().setUp()

    def test_retrieve(self):
        user = User.objects.create_user(username="testuser", password="123", email="test@weni.ai")
        project = Project.objects.create(name="Temba", timezone="Africa/Kigali", created_by=user, modified_by=user)

        Flow.create(org=project.org, name="Flow test", user=user)

        active_flows = project.flows.filter(is_active=True, is_archived=False).exclude(is_system=True).count()
        active_classifiers = project.classifiers.filter(is_active=True).count()
        active_contacts = project.contacts.filter(is_active=True).count()

        statistic_request = self.request_detail(uuid=str(project.project_uuid)).json()

        self.assertEqual(statistic_request["active_flows"], active_flows)
        self.assertEqual(statistic_request["active_classifiers"], active_classifiers)
        self.assertEqual(statistic_request["active_contacts"], active_contacts)

    def get_url_namespace(self):
        return "statistic-detail"
