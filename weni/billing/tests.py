from temba.tests import TembaTest
from weni.billing.queries import ActiveContactsQuery
from django.utils import timezone as tz
from django.conf import settings

from temba.orgs.models import Org


class ActiveContactsQueryTest(TembaTest):
    def setUp(self):
        super().setUp()
        self.query = ActiveContactsQuery
        self.start = tz.now()

        # create some contacts and incoming msgs
        for index in range(10):
            contact = self.create_contact(f"Contact {index+1}", phone=f"+5531248269{index:2d}")
            self.create_incoming_msg(contact, "Hi there")

        # some other contacts out of time range filter
        for index in range(10, 15):
            contact = self.create_contact(f"Contact {index+1}", phone=f"+5531248269{index:2d}")
            self.create_incoming_msg(contact, "Hi there", created_on=self.start - tz.timedelta(minutes=10))

        self.another_org = Org.objects.create(
            name="Weni",
            timezone=tz.pytz.timezone("America/Sao_Paulo"),
            brand=settings.DEFAULT_BRAND,
            created_by=self.user,
            modified_by=self.user,
        )

    def test_total(self):
        self.assertEqual(self.query.total(self.org.uuid, tz.now(), self.start), 10)
        self.assertEqual(self.query.total(self.org.uuid, tz.now(), self.start - tz.timedelta(minutes=11)), 15)
        self.assertEqual(self.query.total(self.another_org.uuid, tz.now(), self.start), 0)
