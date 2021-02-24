from django.contrib.auth.models import User

from django_grpc_framework.test import FakeRpcError, RPCTransactionTestCase

from weni.user_grpc.grpc_gen import user_pb2
from weni.user_grpc.grpc_gen import user_pb2_grpc

from temba.orgs.models import Org


class UserServiceTest(RPCTransactionTestCase):

    WRONG_ID = -1

    def setUp(self):
        User.objects.create_user(username="testuser", password="123", email="test@weni.ai")

        user = User.objects.first()

        Org.objects.create(name="Weni", timezone="America/Maceio", created_by=user, modified_by=user)

        super().setUp()

        self.stub = user_pb2_grpc.UserPermissionControllerStub(self.channel)

    def test_empty_args(self):
        with self.assertRaisesMessage(FakeRpcError, "Org pk cannot be 0 or None"):
            self.user_permission_retrieve_request()

        with self.assertRaisesMessage(FakeRpcError, "User pk cannot be 0 or None"):
            org = Org.objects.first()
            self.user_permission_retrieve_request(org_id=org.id)

    def test_user_permission_retrieve(self):
        org = Org.objects.first()
        user = User.objects.first()

        def permission_is_unique_true(response, permission: str) -> bool:
            permissions = {
                "administrator": response.administrator,
                "viewer": response.viewer,
                "editor": response.editor,
                "surveyor": response.surveyor,
            }
            false_valeues = [key for key, value in permissions.items() if not value]

            return len(false_valeues) == 3 and permission not in false_valeues

        org.administrators.add(user)

        response = self.user_permission_retrieve_request(org_id=org.id, user_id=user.id)

        self.assertTrue(response.administrator)
        self.assertTrue(permission_is_unique_true(response, "administrator"))

        org.administrators.remove(user)
        org.viewers.add(user)

        response = self.user_permission_retrieve_request(org_id=org.id, user_id=user.id)

        self.assertTrue(response.viewer)
        self.assertTrue(permission_is_unique_true(response, "viewer"))

        org.viewers.remove(user)
        org.editors.add(user)

        response = self.user_permission_retrieve_request(org_id=org.id, user_id=user.id)

        self.assertTrue(response.editor)
        self.assertTrue(permission_is_unique_true(response, "editor"))

        org.editors.remove(user)
        org.surveyors.add(user)

        response = self.user_permission_retrieve_request(org_id=org.id, user_id=user.id)

        self.assertTrue(response.surveyor)
        self.assertTrue(permission_is_unique_true(response, "surveyor"))

    def user_permission_retrieve_request(self, **kwargs):
        return self.stub.Retrieve(user_pb2.UserPermissionRetrieveRequest(**kwargs))
