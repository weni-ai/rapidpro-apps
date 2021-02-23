from django.contrib.auth.models import User

from django_grpc_framework.test import FakeRpcError, RPCTransactionTestCase

from weni.user_grpc.grpc_gen import user_pb2
from weni.user_grpc.grpc_gen import user_pb2_grpc

from temba.orgs.models import Org

class UserServiceTest(RPCTransactionTestCase):

    WRONG_ID = -1

    def setUp(self):
        User.objects.create_user(
            username="testuser", password="123", email="test@weni.ai"
        )

        user = User.objects.first()

        Org.objects.create(
            name="Weni",
            timezone="America/Maceio",
            created_by=user,
            modified_by=user
        )

    def test_user_retrieve(self):
        org = Org.objects.first()
        user = User.objects.first()
