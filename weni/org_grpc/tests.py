from django.contrib.auth.models import User

from rest_framework.exceptions import ValidationError

from django_grpc_framework.test import FakeRpcError, RPCTransactionTestCase
import org_pb2
import org_pb2_grpc

from temba.orgs.models import Org


class OrgServiceTest(RPCTransactionTestCase):

    def setUp(self):

        User.objects.create_user(
            username="testuser", password="123", email="test@weni.ai"
        )
        User.objects.create_user(
            username="weniuser", password="123", email='wene@user.com'
        )

        user = User.objects.get(username="testuser")

        Org.objects.create(
            name="Temba",
            timezone="Africa/Kigali",
            created_by=user,
            modified_by=user
        )
        Org.objects.create(
            name="Weni",
            timezone="Africa/Kigali",
            created_by=user,
            modified_by=user
        )
        Org.objects.create(
            name="Test",
            timezone="Africa/Kigali",
            created_by=user,
            modified_by=user
        )

        super().setUp()

        self.stub = org_pb2_grpc.OrgControllerStub(self.channel)

    def test_list_orgs(self):

        with self.assertRaises(FakeRpcError):
            for org in self.stub_org_list_request():
                ...

        with self.assertRaises(FakeRpcError):
            for org in self.stub_org_list_request(user_email="wrong@email.com"):
                ...

        orgs = Org.objects.all()
        user = User.objects.get(username="testuser")

        self.assertEquals(self.get_orgs_count(user), 0)

        orgs[0].administrators.add(user)
        self.assertEquals(self.get_orgs_count(user), 1)

        orgs[1].viewers.add(user)
        self.assertEquals(self.get_orgs_count(user), 2)

        orgs[2].editors.add(user)
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

        with self.assertRaises(ValidationError):
            self.stub.Create(org_pb2.OrgCreateRequest(
                name=org_name, timezone="Africa/Kigali", user_id=50))

        with self.assertRaises(ValidationError):
            self.stub.Create(org_pb2.OrgCreateRequest(
                name=org_name, timezone="Wrong/Zone", user_id=user.id))

        self.stub.Create(org_pb2.OrgCreateRequest(
            name=org_name, timezone="Africa/Kigali", user_id=user.id))

        orgs = Org.objects.filter(name=org_name)
        org = orgs.first()

        self.assertEquals(len(orgs), 1)

        created_by = org.created_by
        modified_by = org.modified_by

        self.assertEquals(created_by, user)
        self.assertEquals(modified_by, user)

    def test_destroy_org(self):
        org = Org.objects.first()
        is_active = org.is_active
        modified_by = org.modified_by

        with self.assertRaisesMessage(FakeRpcError, 'User: 999 not found!'):
            self.stub.Destroy(org_pb2.OrgDestroyRequest(
                id=org.id, user_id=999))

        weniuser = User.objects.get(username="weniuser")

        with self.assertRaisesMessage(FakeRpcError, 'Org: 999 not found!'):
            self.stub.Destroy(org_pb2.OrgDestroyRequest(
                id=999, user_id=weniuser.id))

        self.stub.Destroy(org_pb2.OrgDestroyRequest(
            id=org.id, user_id=weniuser.id))

        destroyed_org = Org.objects.get(id=org.id)

        self.assertFalse(destroyed_org.is_active)
        self.assertNotEquals(is_active, destroyed_org.is_active)
        self.assertEquals(weniuser, destroyed_org.modified_by)
        self.assertNotEquals(modified_by, destroyed_org.modified_by)

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
