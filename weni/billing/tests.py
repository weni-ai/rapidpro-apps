from django_grpc_framework.test import FakeRpcError, RPCTransactionTestCase
from temba.tests import TembaTest
from weni.billing.queries import ActiveContactsQuery


class ActiveContactsQueryTest(TembaTest):
    def setUp(self):
        super().setUp()
        self.query = ActiveContactsQuery

    def test_total(self):
        assert self.query.total() == 42
