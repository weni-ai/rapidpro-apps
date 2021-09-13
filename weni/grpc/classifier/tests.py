from django.contrib.auth.models import User

from django_grpc_framework import test as grpc_test

from temba.orgs.models import Org
from temba.classifiers.models import Classifier, Intent
from temba.classifiers.types.wit import WitType
from temba.classifiers.types.luis import LuisType
from weni.protobuf.flows import classifier_pb2, classifier_pb2_grpc


def get_test_classifier(test: grpc_test.RPCTransactionTestCase) -> Classifier:
    """
    creates a new classifier object containing an intention and returns it.
    """
    response = test.classifier_create_request(
            classifier_type="Test Type",
            user=test.admin.email,
            org=str(test.org.uuid),
            name="Test Name",
            access_token=test.config["access_token"]
        )

    classifier = Classifier.objects.get(uuid=response.uuid)

    Intent.objects.create(classifier=classifier, name="Test Intent", external_id="FakeExternal")

    return classifier


class BaseClassifierServiceTest(grpc_test.RPCTransactionTestCase):

    def setUp(self):
        self.config = {"access_token": "hbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"}

        self.admin = User.objects.create_user(
            username="testuser", password="123", email="test@weni.ai", is_superuser=True
        )

        self.org = Org.objects.create(name="Weni", timezone="America/Maceio", created_by=self.admin, modified_by=self.admin)

        super().setUp()

        self.stub = classifier_pb2_grpc.ClassifierControllerStub(self.channel)

    def classifier_list_request(self, **kwargs):
        return self.stub.List(classifier_pb2.ClassifierListRequest(**kwargs))

    def classifier_create_request(self, **kwargs):
        return self.stub.Create(classifier_pb2.ClassifierCreateRequest(**kwargs))

    def classifier_retrieve_request(self, **kwargs):
        return self.stub.Retrieve(classifier_pb2.ClassifierRetrieveRequest(**kwargs))

    def classifier_destroy_request(self, **kwargs):
        return self.stub.Destroy(classifier_pb2.ClassifierDestroyRequest(**kwargs))


class ClassifierServiceTest(BaseClassifierServiceTest):

    def test_list_classifier(self):
        org = Org.objects.first()
        org_uuid = str(org.uuid)

        classifier = Classifier.create(org, self.admin, WitType.slug, "Booker", self.config, sync=False)

        response = self.classifier_list_request(org_uuid=org_uuid, is_active=True)
        messages = [message for message in response]

        self.assertEqual(len(messages), 1)

        message = messages[0]

        self.assertEqual(message.name, "Booker")
        self.assertEqual(message.classifier_type, WitType.slug)
        self.assertEqual(message.uuid, str(classifier.uuid))
        self.assertEqual(message.access_token, self.config["access_token"])

        classifier = Classifier.create(org, self.admin, LuisType.slug, "Test", self.config, sync=False)

        response = self.classifier_list_request(org_uuid=org_uuid, is_active=True)
        messages = [message for message in response]

        self.assertEqual(len(messages), 2)

        message = messages[0]

        self.assertEqual(message.name, "Test")
        self.assertEqual(message.classifier_type, LuisType.slug)
        self.assertEqual(message.uuid, str(classifier.uuid))
        self.assertEqual(message.access_token, self.config["access_token"])

        response = self.classifier_list_request(org_uuid=org_uuid, is_active=True, classifier_type=LuisType.slug)
        messages = [message for message in response]

        self.assertEqual(len(messages), 1)

        message = messages[0]

        self.assertEqual(message.name, "Test")
        self.assertEqual(message.classifier_type, LuisType.slug)
        self.assertEqual(message.uuid, str(classifier.uuid))
        self.assertEqual(message.access_token, self.config["access_token"])

        classifier = Classifier.create(org, self.admin, LuisType.slug, "Test2", self.config, sync=False)

        response = self.classifier_list_request(org_uuid=org_uuid, is_active=True, classifier_type=LuisType.slug)
        messages = [message for message in response]

        self.assertEqual(len(messages), 2)

        response = self.classifier_list_request(org_uuid=org_uuid, is_active=True)
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

    def test_retrieve_classifier_by_valid_uuid(self):
        classifier = get_test_classifier(self)
        response = self.classifier_retrieve_request(uuid=str(classifier.uuid))

        self.assertEqual(classifier.classifier_type, response.classifier_type)
        self.assertEqual(classifier.name, response.name)
        self.assertEqual(classifier.config["access_token"], response.access_token)
        self.assertEqual(classifier.is_active, response.is_active)

    def test_retrieve_classifier_by_invalid_uuid(self):
        invalid_uuid = "wrong-wrong-wrong-wrong"

        with self.assertRaises(grpc_test.FakeRpcError):
            self.classifier_retrieve_request(uuid=invalid_uuid)


class ClassifierServiceDestroyTest(BaseClassifierServiceTest):

    def test_destroy_classifier_by_valid_uuid(self):
        classifier = get_test_classifier(self)
        self.assertEqual(classifier.intents.count(), 1)

        self.classifier_destroy_request(uuid=str(classifier.uuid), user_email=self.admin.email)

        classifier = Classifier.objects.get(uuid=classifier.uuid)
        self.assertEqual(classifier.intents.count(), 0)
        self.assertFalse(classifier.is_active)

    def test_destroy_classifier_by_invalid_uuid(self):
        invalid_uuid = "wrong-wrong-wrong-wrong"

        with self.assertRaises(grpc_test.FakeRpcError):
            self.classifier_destroy_request(uuid=invalid_uuid, user_email=self.admin.email)
