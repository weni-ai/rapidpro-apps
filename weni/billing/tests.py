import uuid

from django.conf import settings
from django.test.testcases import TestCase
from django.utils import timezone as tz
from google.protobuf.timestamp_pb2 import Timestamp as TimestampMessage
from rest_framework.exceptions import ErrorDetail
from temba.orgs.models import Org
from temba.tests import TembaTest
from weni.billing.grpc_gen.billing_pb2 import BillingRequest
from weni.billing.queries import ActiveContactsQuery
from weni.billing.serializers import BillingRequestSerializer


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


class BillingRequestSerializerTest(TestCase):
    @classmethod
    def create_message(cls, org_uuid=None, before=None, after=None):
        if not org_uuid:
            org_uuid = uuid.uuid4()
        if not before:
            before = tz.now()
        if not after:
            after = tz.now() - tz.timedelta(minutes=1)

        before_message = TimestampMessage()
        before_message.FromDatetime(before)
        after_message = TimestampMessage()
        after_message.FromDatetime(after)

        return BillingRequest(org_uuid=str(org_uuid), before=before_message, after=after_message)

    @classmethod
    def setUpTestData(cls):
        cls.serializer_class = BillingRequestSerializer
        org_uuid = uuid.uuid4()
        before = tz.now()
        after = before - tz.timedelta(minutes=1)
        before_message = TimestampMessage()
        after_message = TimestampMessage()
        before_message.FromDatetime(before)
        after_message.FromDatetime(after)
        cls.valid_data = dict(org_uuid=org_uuid, before=before, after=after)
        cls.valid_message = BillingRequest(org_uuid=str(org_uuid), before=before_message, after=after_message)

    def test_serialize(self):
        serializer = BillingRequestSerializer(self.valid_data)
        self.assertEqual(serializer.message, self.valid_message)

    def test_deserialize(self):
        deserializer = BillingRequestSerializer(message=self.valid_message)
        self.assertTrue(deserializer.is_valid())
        self.assertEqual(dict(deserializer.validated_data), self.valid_data)

    def test_serialize_empty(self):
        with self.assertRaisesMessage(KeyError, "org_uuid"):
            serializer = BillingRequestSerializer(dict(before=tz.now(), after=tz.now()))
            self.assertIsInstance(serializer.message, BillingRequest)

        with self.assertRaisesRegex(KeyError, "before"):
            serializer = BillingRequestSerializer(dict(org_uuid="dontmatternow", after=tz.now()))
            self.assertIsInstance(serializer.message, BillingRequest)

        with self.assertRaisesRegex(KeyError, "after"):
            serializer = BillingRequestSerializer(dict(org_uuid="dontmatternow", before=tz.now()))
            self.assertIsInstance(serializer.message, BillingRequest)

    def test_required(self):
        serializer = BillingRequestSerializer(message=BillingRequest())
        self.assertFalse(serializer.is_valid())
        self.assertIn("org_uuid", serializer.errors)
        self.assertIn("before", serializer.errors)
        self.assertIn("after", serializer.errors)

    def test_invalid_uuid(self):
        message = self.create_message(org_uuid="123")
        serializer = BillingRequestSerializer(message=message)
        self.assertFalse(serializer.is_valid())
        self.assertIn("org_uuid", serializer.errors)
        self.assertEqual(len(serializer.errors["org_uuid"]), 1)
        self.assertEqual(serializer.errors["org_uuid"][0], ErrorDetail(string="Must be a valid UUID.", code="invalid"))

    def test_invalid_after(self):
        msg = self.create_message(after=tz.now() + tz.timedelta(hours=1), before=tz.now() + tz.timedelta(hours=2))
        serializer = self.serializer_class(message=msg)
        self.assertFalse(serializer.is_valid())
        self.assertNotIn("before", serializer.errors)
        self.assertNotIn("org_uuid", serializer.errors)
        self.assertIn("after", serializer.errors)
        self.assertEqual(len(serializer.errors["after"]), 1)
        self.assertEqual(
            serializer.errors["after"][0], ErrorDetail(string="Cannot search after this date.", code="invalid")
        )

    def test_reversed_dates(self):
        msg = self.create_message(before=tz.now() - tz.timedelta(hours=12), after=tz.now())
        serializer = self.serializer_class(message=msg)
        self.assertFalse(serializer.is_valid())
        errors = serializer.errors
        self.assertIn("non_field_errors", errors)
        self.assertEqual(len(errors.keys()), 1)
        self.assertEqual(
            errors["non_field_errors"][0],
            ErrorDetail(string='"after" should be earlier then "before"', code="invalid"),
        )
