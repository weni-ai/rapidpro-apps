from django import db
from django.contrib.auth.models import User

import grpc
from django_grpc_framework.test import RPCTestCase, FakeRpcError, RPCTransactionTestCase
import org_pb2, org_pb2_grpc

from temba.orgs.models import Org

class OrgServiceTest(RPCTransactionTestCase):

    def setUp(self):
        self.user_email = "test@weni.com"

        self.user = User.objects.create_user(
            username="testuser",
            password="123",
            email= self.user_email
        )

        self.orgs = [
            Org.objects.create(
                name="Temba",
                timezone="Africa/Kigali",
                created_by=self.user,
                modified_by=self.user
            ),
            Org.objects.create(
                name="Weni",
                timezone="Africa/Kigali",
                created_by=self.user,
                modified_by=self.user
            ),
            Org.objects.create(
                name="Test",
                timezone="Africa/Kigali",
                created_by=self.user,
                modified_by=self.user
            )
        ]

        super().setUp()

        self.stub = org_pb2_grpc.OrgControllerStub(self.channel)
    
    def test_list_orgs(self):
        
        with self.assertRaises(FakeRpcError):
            for org in self.stub_org_list_request():
                ...

        with self.assertRaises(FakeRpcError):
            for org in self.stub_org_list_request(user_email="wrong@email.com"):
                ...

        orgs = self.orgs

        self.assertEquals(self.get_orgs_count(), 0)

        orgs[0].administrators.add(self.user)
        self.assertEquals(self.get_orgs_count(), 1)

        orgs[1].viewers.add(self.user)
        self.assertEquals(self.get_orgs_count(), 2)

        orgs[2].editors.add(self.user)
        self.assertEquals(self.get_orgs_count(), 3)
    
    def get_orgs_count(self) -> int:
        return len(
            list(self.stub_org_list_request(user_email=self.user_email))
        )

    def stub_org_list_request(self, **kwargs):
        return self.stub.List(org_pb2.OrgListRequest(**kwargs))