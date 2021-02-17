from django.contrib.auth.models import User

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
