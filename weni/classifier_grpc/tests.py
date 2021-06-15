from django.contrib.auth.models import User

from django_grpc_framework.test import RPCTransactionTestCase

from temba.orgs.models import Org
from temba.classifiers.models import Classifier
from temba.classifiers.types.wit import WitType
from temba.classifiers.types.luis import LuisType
from weni.classifier_grpc.grpc_gen import classifier_pb2, classifier_pb2_grpc


class BaseClassifierServiceTest(RPCTransactionTestCase):

    def setUp(self):
        self.config = {"access_token": "hbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"}

        self.admin = User.objects.create_user(
            username="testuser", password="123", email="test@weni.ai", is_superuser=True
        )

        Org.objects.create(name="Weni", timezone="America/Maceio", created_by=self.admin, modified_by=self.admin)

        super().setUp()

        self.stub = classifier_pb2_grpc.ClassifierControllerStub(self.channel)

    def classifier_list_request(self, **kwargs):
        return self.stub.List(classifier_pb2.ClassifierListRequest(**kwargs))

    def classifier_create_request(self, **kwargs):
        return self.stub.Create(classifier_pb2.ClassifierCreateRequest(**kwargs))

    def classifier_retrieve_request(self, **kwargs):
        return self.stub.Retrieve(classifier_pb2.ClassifierRetrieveRequest(**kwargs))


class ClassifierServiceTest(BaseClassifierServiceTest):

    def test_list_classifier(self):
        org = Org.objects.first()
        org_uuid = str(org.uuid)

        classifier = Classifier.create(org, self.admin, WitType.slug, "Booker", self.config, sync=False)

        response = self.classifier_list_request(org_uuid=org_uuid)
        messages = [message for message in response]

        self.assertEqual(len(messages), 1)

        message = messages[0]

        self.assertEqual(message.name, "Booker")
        self.assertEqual(message.classifier_type, WitType.slug)
        self.assertEqual(message.uuid, str(classifier.uuid))
        self.assertEqual(message.access_token, self.config["access_token"])

        classifier = Classifier.create(org, self.admin, LuisType.slug, "Test", self.config, sync=False)

        response = self.classifier_list_request(org_uuid=org_uuid)
        messages = [message for message in response]

        self.assertEqual(len(messages), 2)

        message = messages[0]

        self.assertEqual(message.name, "Test")
        self.assertEqual(message.classifier_type, LuisType.slug)
        self.assertEqual(message.uuid, str(classifier.uuid))
        self.assertEqual(message.access_token, self.config["access_token"])

        response = self.classifier_list_request(org_uuid=org_uuid, classifier_type=LuisType.slug)
        messages = [message for message in response]

        self.assertEqual(len(messages), 1)

        message = messages[0]

        self.assertEqual(message.name, "Test")
        self.assertEqual(message.classifier_type, LuisType.slug)
        self.assertEqual(message.uuid, str(classifier.uuid))
        self.assertEqual(message.access_token, self.config["access_token"])

        classifier = Classifier.create(org, self.admin, LuisType.slug, "Test2", self.config, sync=False)

        response = self.classifier_list_request(org_uuid=org_uuid, classifier_type=LuisType.slug)
        messages = [message for message in response]

        self.assertEqual(len(messages), 2)

        response = self.classifier_list_request(org_uuid=org_uuid)
        messages = [message for message in response]

        self.assertEqual(len(messages), 3)

    def test_create_classifier(self):
        org = Org.objects.first()
        user = self.admin
        access_token = self.config["access_token"]

        name = "Test Name"
        classifier_type = "Test Type"

        response = self.classifier_create_request(
            classifier_type=classifier_type,
            user=user.email,
            org=str(org.uuid),
            name=name,
            access_token=access_token
        )

        self.assertEqual(response.name, name)
        self.assertEqual(response.classifier_type, classifier_type)
        self.assertEqual(response.access_token, access_token)


class ClassifierServiceRetrieveTest(BaseClassifierServiceTest):

    def setUp(self):
        super().setUp()

        org = Org.objects.first()
        access_token = self.config["access_token"]

        self.classifier_create_request(
            classifier_type="Test Type",
            user=self.admin.email,
            org=str(org.uuid),
            name="Test Name",
            access_token=access_token
        )

    def test_ok(self):
        classifier = Classifier.objects.first()
        response = self.classifier_retrieve_request(uuid=str(classifier.uuid))
