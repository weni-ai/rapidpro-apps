from datetime import datetime
import random

from django.contrib.auth.models import User
from django.conf import settings
from django_grpc_framework.test import FakeRpcError, RPCTransactionTestCase
from rest_framework.exceptions import ValidationError

from temba.orgs.models import Org
from weni.protobuf.flows import org_pb2, org_pb2_grpc
from weni.grpc.org.serializers import SerializerUtils


class OrgServiceTest(RPCTransactionTestCase):

    WRONG_ID = -1
    WRONG_UUID = "31313-dasda-dasdasd-23123"
    WRONG_EMAIL = "wrong@email.com"

    def setUp(self):

        User.objects.create_user(username="testuser", password="123", email="test@weni.ai")
        User.objects.create_user(username="weniuser", password="123", email="wene@user.com")

        user = User.objects.get(username="testuser")

        Org.objects.create(name="Temba", timezone="Africa/Kigali", created_by=user, modified_by=user)
        Org.objects.create(name="Weni", timezone="Africa/Kigali", created_by=user, modified_by=user)
        Org.objects.create(name="Test", timezone="Africa/Kigali", created_by=user, modified_by=user)

        super().setUp()

        self.stub = org_pb2_grpc.OrgControllerStub(self.channel)

    def test_serializer_utils(self):
        user = User.objects.last()

        with self.assertRaisesMessage(ValidationError, (f"User: {self.WRONG_ID} not found!")):
            SerializerUtils.get_object(User, self.WRONG_ID)

        self.assertEquals(user, SerializerUtils.get_object(User, user.pk))

    def test_list_orgs(self):

        with self.assertRaises(FakeRpcError):
            for org in self.stub_org_list_request():
                ...

        with self.assertRaises(FakeRpcError):
            for org in self.stub_org_list_request(user_email="wrong@email.com"):
                ...

        orgs = Org.objects.all()
        user = User.objects.get(username="testuser")

        weni_org = orgs.get(name="Weni")
        temba_org = orgs.get(name="Temba")
        test_org = orgs.get(name="Test")

        weni_org.administrators.add(user)
        weni_org.is_active = False
        weni_org.save(update_fields=["is_active"])

        self.assertEquals(self.get_orgs_count(user), 0)

        weni_org.is_active = True
        weni_org.save(update_fields=["is_active"])

        self.assertEquals(self.get_orgs_count(user), 1)

        temba_org.viewers.add(user)
        self.assertEquals(self.get_orgs_count(user), 2)

        test_org.editors.add(user)
        self.assertEquals(self.get_orgs_count(user), 3)

    def test_list_users_on_org(self):
        org = Org.objects.get(name="Temba")

        testuser = User.objects.get(username="testuser")
        weniuser = User.objects.get(username="weniuser")

        org.administrators.add(testuser)
        self.assertEquals(self.get_org_users_count(testuser), 1)

        org.administrators.add(weniuser)
        self.assertEquals(self.get_org_users_count(testuser), 2)

    def test_create_org(self):
        org_name = "TestCreateOrg"
        user = User.objects.first()

        with self.assertRaisesMessage(ValidationError, '"Wrong/Zone" is not a valid choice.'):
            self.stub.Create(org_pb2.OrgCreateRequest(name=org_name, timezone="Wrong/Zone", user_email=user.email))

        self.stub.Create(
            org_pb2.OrgCreateRequest(name=org_name, timezone="Africa/Kigali", user_email="newemail@email.com")
        )

        newuser_qs = User.objects.filter(email="newemail@email.com")

        self.assertTrue(newuser_qs.exists())

        newuser = newuser_qs.first()

        orgs = Org.objects.filter(name=org_name)
        org = orgs.first()

        self.assertEquals(orgs.count(), 1)

        created_by = org.created_by
        modified_by = org.modified_by
        administrators = org.administrators.all()
        administrator = administrators.get(pk=newuser.pk)

        self.assertEquals(created_by, newuser)
        self.assertEquals(modified_by, newuser)
        self.assertFalse(org.uses_topups)

        self.assertEquals(administrators.count(), 1)
        self.assertEquals(administrator, newuser)

        self.stub.Create(
            org_pb2.OrgCreateRequest(name="neworg", timezone="Africa/Kigali", user_email="newemail@email.com")
        )

        self.assertEqual(User.objects.filter(email="newemail@email.com").count(), 1)

    def test_retrieve_org(self):
        org = Org.objects.last()
        user = User.objects.last()

        permission_types = ("administrator", "viewer", "editor", "surveyor")

        random_permission = random.choice(permission_types)

        if random_permission == "administrator":
            org.administrators.add(user)
        if random_permission == "viewer":
            org.viewers.add(user)
        if random_permission == "editor":
            org.editors.add(user)
        if random_permission == "surveyor":
            org.surveyors.add(user)

        org_uuid = str(org.uuid)
        org_timezone = str(org.timezone)

        with self.assertRaisesMessage(FakeRpcError, f"Org: {self.WRONG_UUID} not found!"):
            self.org_retrieve_request(uuid=self.WRONG_UUID)

        response = self.org_retrieve_request(uuid=org_uuid)
        response_user = response.users[0]

        self.assertEqual(response.id, org.id)
        self.assertEqual(response.name, org.name)
        self.assertEqual(response.uuid, org_uuid)
        self.assertEqual(org_timezone, response.timezone)
        self.assertEqual(org.date_format, response.date_format)

        self.assertEqual(user.id, response_user.id)
        self.assertEqual(user.email, response_user.email)
        self.assertEqual(user.username, response_user.username)

        self.assertEqual(response_user.permission_type, random_permission)

    def test_destroy_org(self):
        org = Org.objects.last()
        is_active = org.is_active
        modified_by = org.modified_by

        with self.assertRaisesMessage(FakeRpcError, f"User: {self.WRONG_EMAIL} not found!"):
            self.stub.Destroy(org_pb2.OrgDestroyRequest(uuid=str(org.uuid), user_email=self.WRONG_EMAIL))

        weniuser = User.objects.get(username="weniuser")

        with self.assertRaisesMessage(FakeRpcError, f"Org: {self.WRONG_UUID} not found!"):
            self.stub.Destroy(org_pb2.OrgDestroyRequest(uuid=self.WRONG_UUID, user_email=weniuser.email))

        self.stub.Destroy(org_pb2.OrgDestroyRequest(uuid=str(org.uuid), user_email=weniuser.email))

        destroyed_org = Org.objects.get(id=org.id)

        self.assertFalse(destroyed_org.is_active)
        self.assertNotEquals(is_active, destroyed_org.is_active)
        self.assertEquals(weniuser, destroyed_org.modified_by)
        self.assertNotEquals(modified_by, destroyed_org.modified_by)

    def test_update_org(self):
        org = Org.objects.first()
        user = User.objects.first()

        permission_error_message = f"User: {user.id} has no permission to update Org: {org.uuid}"

        with self.assertRaisesMessage(FakeRpcError, permission_error_message):
            self.stub.Update(org_pb2.OrgUpdateRequest(uuid=str(org.uuid), modified_by=user.email))

        user.is_superuser = True
        user.save()

        org.administrators.add(user)

        update_fields = {
            "name": "NewOrgName",
            "timezone": "America/Maceio",
            "date_format": "M",
            "plan": settings.INFINITY_PLAN,
            "plan_end": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "brand": "push.ia",
            "is_anon": True,
            "is_multi_user": True,
            "is_multi_org": True,
            "is_suspended": True,
        }

        self.stub.Update(org_pb2.OrgUpdateRequest(uuid=str(org.uuid), modified_by=user.email, **update_fields))

        updated_org = Org.objects.get(pk=org.pk)

        self.assertEquals(update_fields.get("name"), updated_org.name)
        self.assertNotEquals(org.name, updated_org.name)

        self.assertEquals(update_fields.get("timezone"), str(updated_org.timezone))
        self.assertNotEquals(org.timezone, updated_org.timezone)

        self.assertEquals(update_fields.get("date_format"), updated_org.date_format)
        self.assertNotEquals(org.date_format, updated_org.date_format)

        self.assertEquals(updated_org.plan, settings.INFINITY_PLAN)
        self.assertNotEquals(org.plan, updated_org.plan)
        self.assertFalse(updated_org.uses_topups)
        self.assertEquals(updated_org.plan_end, None)

        self.assertEquals(update_fields.get("brand"), updated_org.brand)
        self.assertNotEquals(org.brand, updated_org.brand)

        self.assertEquals(update_fields.get("is_anon"), updated_org.is_anon)
        self.assertNotEquals(org.is_anon, updated_org.is_anon)

        self.assertEquals(update_fields.get("is_multi_user"), updated_org.is_multi_user)
        self.assertNotEquals(org.is_multi_user, updated_org.is_multi_user)

        self.assertEquals(update_fields.get("is_multi_org"), updated_org.is_multi_org)
        self.assertNotEquals(org.is_multi_org, updated_org.is_multi_org)

        self.assertEquals(update_fields.get("is_suspended"), updated_org.is_suspended)
        self.assertNotEquals(org.is_suspended, updated_org.is_suspended)

    def get_org_users_count(self, user: User) -> int:
        orgs = self.get_user_orgs(user)
        org = next(orgs)
        return len(org.users)

    def get_orgs_count(self, user: User) -> int:
        return len(list(self.get_user_orgs(user)))

    def get_user_orgs(self, user: User):
        return self.stub_org_list_request(user_email=user.email)

    def stub_org_list_request(self, **kwargs):
        return self.stub.List(org_pb2.OrgListRequest(**kwargs))

    def org_retrieve_request(self, **kwargs):
        return self.stub.Retrieve(org_pb2.OrgRetrieveRequest(**kwargs))
