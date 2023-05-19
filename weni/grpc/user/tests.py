from django.conf import settings
from django.contrib.auth.models import User

from django_grpc_framework.test import FakeRpcError, RPCTransactionTestCase

from weni.protobuf.flows import user_pb2
from weni.protobuf.flows import user_pb2_grpc

from temba.orgs.models import Org


class UserServiceTest(RPCTransactionTestCase):
    WRONG_EMAIL = "wrong@wrong.wrong"
    WRONG_UUID = "wrong-wrong-wrong-wrong-wrong."

    def setUp(self):
        User.objects.create_user(
            username="testuser",
            password="123",
            email="test@weni.ai",
            first_name="Weni",
            last_name="ai",
        )

        user = User.objects.first()

        Org.objects.create(name="Weni", timezone="America/Maceio", created_by=user, modified_by=user)

        super().setUp()

        self.user_permission_stub = user_pb2_grpc.UserPermissionControllerStub(self.channel)
        self.user_stub = user_pb2_grpc.UserControllerStub(self.channel)

    def test_retrieve_permission_with_non_existent_user(self):
        org = Org.objects.first()
        email = "nonexistent@email.com"

        response = self.user_permission_retrieve_request(org_uuid=str(org.uuid), user_email=email)

        self.assertTrue(User.objects.filter(email=email).exists())

        self.assertFalse(response.administrator)
        self.assertFalse(response.viewer)
        self.assertFalse(response.editor)
        self.assertFalse(response.surveyor)
        self.assertFalse(response.agent)

    def test_update_permission_with_non_existent_user(self):
        org = Org.objects.first()
        email = "nonexistent@email.com"

        response = self.user_permission_update_request(
            org_uuid=str(org.uuid), user_email=email, permission="administrator"
        )

        self.assertTrue(User.objects.filter(email=email).exists())

        self.assertTrue(response.administrator)
        self.assertFalse(response.viewer)
        self.assertFalse(response.editor)
        self.assertFalse(response.surveyor)
        self.assertFalse(response.agent)

    def test_update_user_lang_with_non_existent_user(self):
        email = "nonexistent@email.com"

        langs = list(map(lambda lang: lang[0], settings.LANGUAGES))
        _ = self.user_language_update_request(email=email, language=langs[0])

        user = User.objects.get(email=email)
        self.assertEquals(user.get_settings().language, langs[0])

    def test_user_permission_retrieve(self):
        org = Org.objects.first()
        user = User.objects.first()

        with self.assertRaisesMessage(FakeRpcError, f"Org: {self.WRONG_UUID} not found!"):
            self.user_permission_retrieve_request(org_uuid=self.WRONG_UUID, user_email=self.WRONG_EMAIL)

        org.administrators.add(user)

        response = self.user_permission_retrieve_request(org_uuid=str(org.uuid), user_email=user.email)

        self.assertTrue(response.administrator)
        self.assertTrue(self.permission_is_unique_true(response, "administrator"))

        org.administrators.remove(user)
        org.viewers.add(user)

        response = self.user_permission_retrieve_request(org_uuid=str(org.uuid), user_email=user.email)

        self.assertTrue(response.viewer)
        self.assertTrue(self.permission_is_unique_true(response, "viewer"))

        org.viewers.remove(user)
        org.editors.add(user)

        response = self.user_permission_retrieve_request(org_uuid=str(org.uuid), user_email=user.email)

        self.assertTrue(response.editor)
        self.assertTrue(self.permission_is_unique_true(response, "editor"))

        org.editors.remove(user)
        org.surveyors.add(user)

        response = self.user_permission_retrieve_request(org_uuid=str(org.uuid), user_email=user.email)

        self.assertTrue(response.surveyor)
        self.assertTrue(self.permission_is_unique_true(response, "surveyor"))

        org.surveyors.remove(user)
        org.agents.add(user)

        response = self.user_permission_retrieve_request(org_uuid=str(org.uuid), user_email=user.email)

        self.assertTrue(response.agent)
        self.assertTrue(self.permission_is_unique_true(response, "agent"))

    def test_user_retrieve(self):
        user = User.objects.first()

        response = self.user_retrieve_request(email=user.email)

        self.validate_response_user(response, user)

    def test_user_permission_update(self):
        org = Org.objects.first()
        user = User.objects.first()

        with self.assertRaisesMessage(FakeRpcError, "adm is not a valid permission!"):
            self.user_permission_update_request(org_uuid=str(org.uuid), user_email=user.email, permission="adm")

        update_response = self.user_permission_update_request(
            org_uuid=str(org.uuid), user_email=user.email, permission="administrator"
        )
        retrieve_response = self.user_permission_retrieve_request(org_uuid=str(org.uuid), user_email=user.email)

        self.assertEquals(update_response, retrieve_response)

        self.assertTrue(retrieve_response.administrator)
        self.assertTrue(self.permission_is_unique_true(retrieve_response, "administrator"))

        self.user_permission_update_request(org_uuid=str(org.uuid), user_email=user.email, permission="viewer")
        retrieve_response = self.user_permission_retrieve_request(org_uuid=str(org.uuid), user_email=user.email)

        self.assertTrue(retrieve_response.viewer)
        self.assertTrue(self.permission_is_unique_true(retrieve_response, "viewer"))

        self.user_permission_update_request(org_uuid=str(org.uuid), user_email=user.email, permission="editor")
        retrieve_response = self.user_permission_retrieve_request(org_uuid=str(org.uuid), user_email=user.email)

        self.assertTrue(retrieve_response.editor)
        self.assertTrue(self.permission_is_unique_true(retrieve_response, "editor"))

        self.user_permission_update_request(org_uuid=str(org.uuid), user_email=user.email, permission="surveyor")
        retrieve_response = self.user_permission_retrieve_request(org_uuid=str(org.uuid), user_email=user.email)

        self.assertTrue(retrieve_response.surveyor)
        self.assertTrue(self.permission_is_unique_true(retrieve_response, "surveyor"))

        self.user_permission_update_request(org_uuid=str(org.uuid), user_email=user.email, permission="agent")
        retrieve_response = self.user_permission_retrieve_request(org_uuid=str(org.uuid), user_email=user.email)

        self.assertTrue(retrieve_response.agent)
        self.assertTrue(self.permission_is_unique_true(retrieve_response, "agent"))

    def test_user_language_update(self):
        user = User.objects.first()

        languages = [language[0] for language in settings.LANGUAGES]

        with self.assertRaisesMessage(FakeRpcError, "Invalid argument: language"):
            self.user_language_update_request(email=user.email, language="wrong")

        for language in languages:
            self.user_language_update_request(email=user.email, language=language)

            user_language = User.objects.get(pk=user.pk).get_settings().language
            self.assertEqual(user_language, language)

        response = self.user_language_update_request(email=user.email, language=languages[0])

        self.validate_response_user(response, user)

    def test_user_permission_remove(self):
        org = Org.objects.first()
        user = User.objects.first()

        with self.assertRaisesMessage(FakeRpcError, "adm is not a valid permission!"):
            self.user_permission_remove_request(org_uuid=str(org.uuid), user_email=user.email, permission="adm")

        self.user_permission_update_request(org_uuid=str(org.uuid), user_email=user.email, permission="viewer")
        retrieve_response = self.user_permission_retrieve_request(org_uuid=str(org.uuid), user_email=user.email)

        self.user_permission_remove_request(org_uuid=str(org.uuid), user_email=user.email, permission="viewer")
        retrieve_response_removed = self.user_permission_retrieve_request(
            org_uuid=str(org.uuid), user_email=user.email
        )

        self.assertFalse(retrieve_response_removed.viewer)
        self.assertNotEquals(retrieve_response.viewer, retrieve_response_removed.viewer)

    def permission_is_unique_true(self, response, permission: str) -> bool:
        permissions = {
            "administrator": response.administrator,
            "viewer": response.viewer,
            "editor": response.editor,
            "surveyor": response.surveyor,
            "agent": response.agent,
        }
        false_valeues = [key for key, value in permissions.items() if not value]

        return len(false_valeues) == len(permissions.items()) - 1 and permission not in false_valeues

    def validate_response_user(self, response, user: User):
        self.assertEquals(response.id, user.id)
        self.assertEquals(response.username, user.username)
        self.assertEquals(response.email, user.email)
        self.assertEquals(response.first_name, user.first_name)
        self.assertEquals(response.last_name, user.last_name)
        self.assertEquals(response.date_joined, user.date_joined.strftime("%Y-%m-%dT%H:%M:%S.%fZ"))
        self.assertEquals(response.is_active, user.is_active)
        self.assertEquals(response.is_superuser, user.is_superuser)

    def user_permission_retrieve_request(self, **kwargs):
        return self.user_permission_stub.Retrieve(user_pb2.UserPermissionRetrieveRequest(**kwargs))

    def user_permission_update_request(self, **kwargs):
        return self.user_permission_stub.Update(user_pb2.UserPermissionUpdateRequest(**kwargs))

    def user_permission_remove_request(self, **kwargs):
        return self.user_permission_stub.Remove(user_pb2.UserPermissionUpdateRequest(**kwargs))

    def user_retrieve_request(self, **kwargs):
        return self.user_stub.Retrieve(user_pb2.UserRetrieveRequest(**kwargs))

    def user_language_update_request(self, **kwargs):
        return self.user_stub.Update(user_pb2.UpdateUserLang(**kwargs))
