from django.contrib.auth.models import User

from django_grpc_framework.test import FakeRpcError, RPCTransactionTestCase

from temba.orgs.models import Org
from temba.flows.models import Flow

from weni.protobuf.flows import flow_pb2, flow_pb2_grpc


class FlowServiceTest(RPCTransactionTestCase):
    def setUp(self):
        User.objects.create_user(username="testuser", password="123", email="test@weni.ai")

        user = User.objects.first()

        temba = Org.objects.create(name="Temba", timezone="America/Maceio", created_by=user, modified_by=user)
        weni = Org.objects.create(name="Weni", timezone="America/Maceio", created_by=user, modified_by=user)

        Flow.create(name="Test Temba", user=user, org=temba)
        Flow.create(name="Test flow name", user=user, org=weni)
        Flow.create(name="Test Weni flow name", user=user, org=weni)

        super().setUp()

        self.stub = flow_pb2_grpc.FlowControllerStub(self.channel)

    def test_list_flow(self):
        temba = Org.objects.get(name="Temba")
        weni = Org.objects.get(name="Weni")

        with self.assertRaisesMessage(FakeRpcError, "Org: 123 not found!"):
            for flow in self.flow_list_request(flow_name="test", org_uuid="123"):
                ...

        with self.assertRaisesMessage(FakeRpcError, "Org: None not found!"):
            for flow in self.flow_list_request(flow_name="test", org_uuid=None):
                ...

        with self.assertRaisesMessage(FakeRpcError, "Org: None not found!"):
            for flow in self.flow_list_request(flow_name="test", org_uuid=""):
                ...

        response = self.flow_list_request(flow_name="test", org_uuid=str(temba.uuid))

        flows, flows_count = self.get_flows_and_count(response)

        self.assertEquals(flows_count, 1)
        self.assertEquals(flows[0].name, "Test Temba")

        response = self.flow_list_request(flow_name="test", org_uuid=str(weni.uuid))

        flows, flows_count = self.get_flows_and_count(response)

        weni_flow_names = [flow.name for flow in Flow.objects.filter(org=weni.id)]

        self.assertEquals(flows_count, 2)

        for flow in flows:
            self.assertIn(flow.name, weni_flow_names)

        response = self.flow_list_request(flow_name="weni", org_uuid=str(weni.uuid))

        flows, flows_count = self.get_flows_and_count(response)

        self.assertEquals(flows[0].name, "Test Weni flow name")
        self.assertEquals(flows_count, 1)

    def get_flows_and_count(self, response) -> (list, int):
        flows = [flow for flow in response]
        flows_count = len(flows)

        return flows, flows_count

    def flow_list_request(self, **kwargs):
        return self.stub.List(flow_pb2.FlowListRequest(**kwargs))
