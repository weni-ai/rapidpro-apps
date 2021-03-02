from temba.tests import TembaTest
from weni.billing.queries import ActiveContactsQuery


class ActiveContactsQueryTest(TembaTest):
    def setUp(self):
        super().setUp()
        self.query = ActiveContactsQuery

        # create some contacts and incoming msgs
        for index in range(10):
            contact = self.create_contact(f"Contact {index+1}", phone=f"+5531248269{index:2d}")
            self.create_incoming_msg(contact, "Hi there")

    def test_total(self):
        self.assertEqual(self.query.total(), 10)
