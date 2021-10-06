from django.contrib.auth.models import User

from django_grpc_framework import test as test_grpc

from temba.orgs.models import Org
from temba.contacts.models import Contact
from temba.flows.models import Flow
from temba.classifiers.models import Classifier
from temba.tests import mock_mailroom
from temba.utils.management.commands.test_db import DisableTriggersOn

from weni.protobuf.flows import statistic_pb2, statistic_pb2_grpc


class OrgStatisticServiceTest(test_grpc.RPCTransactionTestCase):
    def setUp(self):

        User.objects.create_user(username="testuser", password="123", email="test@weni.ai")
        user = User.objects.get(username="testuser")

        weni = Org.objects.create(name="Weni", timezone="America/Maceio", created_by=user, modified_by=user)

        Flow.create(name="Test Temba", user=user, org=weni, is_active=False)
        Flow.create(name="Test flow name", user=user, org=weni)
        Flow.create(name="Test Weni flow name", user=user, org=weni)

        Classifier.objects.create(org=weni, config="", created_by=user, modified_by=user, is_active=False)
        Classifier.objects.create(org=weni, config="", created_by=user, modified_by=user)
        Classifier.objects.create(org=weni, config="", created_by=user, modified_by=user)

        super().setUp()

        self.stub = statistic_pb2_grpc.OrgStatisticControllerStub(test_grpc.Channel())

    @mock_mailroom
    def test_retrieve_statistic(self, mr_mocks):
        org = Org.objects.first()
        org_uuid = str(org.uuid)

        with self.assertRaisesMessage(test_grpc.FakeRpcError, "Org: 123 not found!"):
            self.org_statistic_list_request(org_uuid="123")

        with DisableTriggersOn(Contact):

            test_contact = Contact.objects.create(name="Test Contact", org=org)
            Contact.objects.create(name="Weni Contact", org=org)

            self.set_obj_active(test_contact, False)

            response = self.org_statistic_list_request(org_uuid=org_uuid)
            self.assertEqual(response.active_contacts, 1)

            self.set_obj_active(test_contact, True)

            response = self.org_statistic_list_request(org_uuid=org_uuid)
            self.assertEqual(response.active_contacts, 2)

        response = self.org_statistic_list_request(org_uuid=org_uuid)
        self.assertEqual(response.active_flows, 2)

        flow = Flow.objects.get(is_active=False)
        self.set_obj_active(flow, True)

        response = self.org_statistic_list_request(org_uuid=org_uuid)
        self.assertEqual(response.active_flows, 3)

        self.assertEqual(response.active_classifiers, 2)

        classifier = Classifier.objects.get(is_active=False)
        self.set_obj_active(classifier, True)

        response = self.org_statistic_list_request(org_uuid=org_uuid)
        self.assertEqual(response.active_classifiers, 3)

    def set_obj_active(self, obj, is_active: bool):
        obj.is_active = is_active
        obj.save(update_fields=["is_active"])

    def org_statistic_list_request(self, **kwargs):
        return self.stub.Retrieve(statistic_pb2.OrgStatisticRetrieveRequest(**kwargs))
