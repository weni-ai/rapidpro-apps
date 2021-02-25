from django.contrib.auth.models import User

from django_grpc_framework.test import FakeRpcError, RPCTransactionTestCase

from weni.user_grpc.grpc_gen import user_pb2
from weni.user_grpc.grpc_gen import user_pb2_grpc

from temba.orgs.models import Org


class UserServiceTest(RPCTransactionTestCase):

    WRONG_ID = -1

    def setUp(self):
        User.objects.create_user(
            username="testuser", password="123", email="test@weni.ai", first_name="Weni", last_name="ai",
        )

        user = User.objects.first()

        Org.objects.create(name="Weni", timezone="America/Maceio", created_by=user, modified_by=user)

        super().setUp()

        self.user_permission_stub = user_pb2_grpc.UserPermissionControllerStub(self.channel)
        self.user_stub = user_pb2_grpc.UserControllerStub(self.channel)

    def test_user_permission_retrieve(self):
        org = Org.objects.first()
        user = User.objects.first()

        with self.assertRaisesMessage(FakeRpcError, f"Org: {self.WRONG_ID} not found!"):
            self.user_permission_retrieve_request(org_id=self.WRONG_ID, user_id=self.WRONG_ID)

        with self.assertRaisesMessage(FakeRpcError, f"User: {self.WRONG_ID} not found!"):
            self.user_permission_retrieve_request(org_id=org.id, user_id=self.WRONG_ID)

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

    def test_user_retrieve(self):
        user = User.objects.first()

        wrong_email = "wrong@email.com"

        with self.assertRaisesMessage(FakeRpcError, f"User: {wrong_email} not found!"):
            self.user_retrieve_request(email=wrong_email)

        response = self.user_retrieve_request(email=user.email)

        self.assertEquals(response.id, user.id)
        self.assertEquals(response.username, user.username)
        self.assertEquals(response.email, user.email)
        self.assertEquals(response.first_name, user.first_name)
        self.assertEquals(response.last_name, user.last_name)
        self.assertEquals(response.date_joined, user.date_joined.strftime("%Y-%m-%dT%H:%M:%S.%fZ"))
        self.assertEquals(response.is_active, user.is_active)
        self.assertEquals(response.is_superuser, user.is_superuser)

    def test_user_permission_update(self):
        org = Org.objects.first()
        user = User.objects.first()

        with self.assertRaisesMessage(FakeRpcError, "adm is not a valid permission!"):
            self.user_permission_update_request(org_id=org.id, user_id=user.id, permission="adm")

        update_response = self.user_permission_update_request(
            org_id=org.id, user_id=user.id, permission="administrator"
        )
        retrieve_response = self.user_permission_retrieve_request(org_id=org.id, user_id=user.id)

        self.assertEquals(update_response, retrieve_response)

        self.assertTrue(retrieve_response.administrator)
        self.assertTrue(self.permission_is_unique_true(retrieve_response, "administrator"))

        self.user_permission_update_request(org_id=org.id, user_id=user.id, permission="viewer")
        retrieve_response = self.user_permission_retrieve_request(org_id=org.id, user_id=user.id)

        self.assertTrue(retrieve_response.viewer)
        self.assertTrue(self.permission_is_unique_true(retrieve_response, "viewer"))

        self.user_permission_update_request(org_id=org.id, user_id=user.id, permission="editor")
        retrieve_response = self.user_permission_retrieve_request(org_id=org.id, user_id=user.id)

        self.assertTrue(retrieve_response.editor)
        self.assertTrue(self.permission_is_unique_true(retrieve_response, "editor"))

        self.user_permission_update_request(org_id=org.id, user_id=user.id, permission="surveyor")
        retrieve_response = self.user_permission_retrieve_request(org_id=org.id, user_id=user.id)

        self.assertTrue(retrieve_response.surveyor)
        self.assertTrue(self.permission_is_unique_true(retrieve_response, "surveyor"))

    def permission_is_unique_true(self, response, permission: str) -> bool:
        permissions = {
            "administrator": response.administrator,
            "viewer": response.viewer,
            "editor": response.editor,
            "surveyor": response.surveyor,
        }
        false_valeues = [key for key, value in permissions.items() if not value]

        return len(false_valeues) == 3 and permission not in false_valeues

    def user_permission_retrieve_request(self, **kwargs):
        return self.user_permission_stub.Retrieve(user_pb2.UserPermissionRetrieveRequest(**kwargs))

    def user_permission_update_request(self, **kwargs):
        return self.user_permission_stub.Update(user_pb2.UserPermissionUpdateRequest(**kwargs))

    def user_retrieve_request(self, **kwargs):
        return self.user_stub.Retrieve(user_pb2.UserRetrieveRequest(**kwargs))
