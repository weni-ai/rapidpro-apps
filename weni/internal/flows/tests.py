import json
from abc import ABC, abstractmethod

from django.contrib.auth.models import Group
from django.urls import reverse
from django.utils.http import urlencode
from django.contrib.auth.models import User

from temba.tests import TembaTest
from temba.api.models import APIToken

from temba.flows.models import Flow
from weni.internal.models import Project
from weni.internal.flows.views import ProjectFlowsViewSet


view = ProjectFlowsViewSet
view.permission_classes = []


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
            url,
            HTTP_AUTHORIZATION=f"Token {token.key}",
            data=json.dumps(data),
            content_type="application/json",
        )

    def request_delete(self, uuid):
        url = self.reverse(self.get_url_namespace(), kwargs={"uuid": uuid})
        token = APIToken.get_or_create(self.org, self.admin, Group.objects.get(name="Administrators"))

        return self.client.delete(f"{url}", HTTP_AUTHORIZATION=f"Token {token.key}")

    @abstractmethod
    def get_url_namespace(self):
        ...


class ListFlowTestCase(TembaTest, TembaRequestMixin):
    def setUp(self):
        User.objects.create_user(username="testuser", password="123", email="test@weni.ai")

        user = User.objects.first()

        temba = Project.objects.create(name="Temba", timezone="America/Maceio", created_by=user, modified_by=user)
        weni = Project.objects.create(name="Weni", timezone="America/Maceio", created_by=user, modified_by=user)

        Flow.create(name="Test Temba", user=user, org=temba)
        Flow.create(name="Test flow name", user=user, org=weni)
        Flow.create(name="Test Weni flow name", user=user, org=weni)

        super().setUp()

    def test_list_flow(self):
        temba = Project.objects.filter(name="Temba").first()
        weni = Project.objects.get(name="Weni")

        response = self.request_get(flow_name="test", org_uuid="123")  # {'org_uuid': ['“123” is not a valid UUID.']}
        self.assertEquals(response.status_code, 400)

        response = self.request_get(flow_name="test", org_uuid="")  # {'org_id': ['This field may not be blank.']}
        self.assertEquals(response.status_code, 400)

        response = self.request_get(flow_name="test", org_uuid=str(temba.project_uuid)).json()
        flows, flows_count = self.get_flows_and_count(response)

        self.assertEquals(flows_count, 1)
        self.assertEquals(flows[0].get("name"), "Test Temba")

        response = self.request_get(flow_name="test", org_uuid=str(weni.project_uuid)).json()

        flows, flows_count = self.get_flows_and_count(response)
        weni_flow_names = [flow.name for flow in Flow.objects.filter(org=weni.id)]

        self.assertEquals(flows_count, 2)

        for flow in flows:
            self.assertIn(flow.get("name"), weni_flow_names)

        response = self.request_get(flow_name="weni", org_uuid=str(weni.project_uuid)).json()

        flows, flows_count = self.get_flows_and_count(response)

        self.assertEquals(flows[0].get("name"), "Test Weni flow name")
        self.assertEquals(flows_count, 1)

    def get_flows_and_count(self, response):
        flows = [flow for flow in response]
        flows_count = len(flows)

        return flows, flows_count

    def get_url_namespace(self):
        return "project-flows-list"
