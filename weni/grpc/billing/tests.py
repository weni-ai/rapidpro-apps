import uuid

from django.conf import settings
from django.test.testcases import TestCase
from django.utils import timezone as tz
from google.protobuf.timestamp_pb2 import Timestamp as TimestampMessage
from rest_framework.exceptions import ErrorDetail
from temba.orgs.models import Org
from temba.tests import TembaTest
from weni.protobuf.flows import billing_pb2 as pb2, billing_pb2_grpc as stubs
from weni.grpc.billing.queries import ActiveContactsQuery
from weni.grpc.billing.serializers import BillingRequestSerializer, ActiveContactDetailSerializer
from django_grpc_framework.test import FakeRpcError, RPCTransactionTestCase


class ActiveContactsQueryTest(TembaTest):
    def setUp(self):
        super().setUp()
        self.query = ActiveContactsQuery
        self.start = tz.now()

        # create some contacts and incoming msgs
        for index in range(10):
            contact = self.create_contact(f"Contact {index+1}", phone=f"+5531248269{index:2d}")
            self.create_outgoing_msg(contact, f"Hello, {contact.name}!")

        # some other contacts out of time range filter
        for index in range(10, 15):
            contact = self.create_contact(f"Contact {index+1}", phone=f"+5531248269{index:2d}")
            self.create_outgoing_msg(
                contact,
                f"Hi there, {contact.name}!",
                created_on=tz.now() - tz.timedelta(minutes=10),
                sent_on=tz.now() - tz.timedelta(minutes=10),
            )

        self.another_org = Org.objects.create(
            name="Weni",
            timezone=tz.pytz.timezone("America/Sao_Paulo"),
            brand=settings.DEFAULT_BRAND,
            created_by=self.user,
            modified_by=self.user,
        )

    def test_total(self):
        self.assertEqual(self.query.total(self.org.uuid, tz.now(), self.start), 10)
        self.assertEqual(
            self.query.total(self.org.uuid, tz.now(), self.start - tz.timedelta(minutes=11)),
            15,
        )
        self.assertEqual(self.query.total(self.another_org.uuid, tz.now(), self.start), 0)

    def test_detailed(self):
        start_to_now = self.query.detailed(self.org.uuid, tz.now(), self.start)
        self.assertEqual(start_to_now.count(), 10)
        for row in start_to_now:
            self.assertEqual(row["msg__text"], f"Hello, {row['name']}!")
            self.assertTrue(row["msg__sent_on"] >= self.start)
            self.assertTrue(row["msg__sent_on"] <= tz.now())

        before_start = self.query.detailed(self.org.uuid, self.start, self.start - tz.timedelta(minutes=10))
        self.assertEqual(before_start.count(), 5)
        for row in before_start:
            self.assertEqual(row["msg__text"], f"Hi there, {row['name']}!")
            self.assertTrue(row["msg__sent_on"] >= self.start - tz.timedelta(minutes=10))
            self.assertTrue(row["msg__sent_on"] <= self.start)

        ten_minutes_ago = self.query.detailed(self.org.uuid, tz.now(), self.start - tz.timedelta(minutes=10))
        self.assertEqual(ten_minutes_ago.count(), 15)

        another_org = self.query.detailed(self.another_org.uuid, tz.now(), self.start)
        self.assertEqual(another_org.count(), 0)


class ActiveContactDetailSerializerTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.serializer_class = ActiveContactDetailSerializer
        contact_uuid = uuid.uuid4()
        contact_name = "Joe"
        msg_uuid = uuid.uuid4()
        msg_text = "Hi, Joe!"

        msg_sent_on = tz.now()
        ts = TimestampMessage()
        ts.FromDatetime(msg_sent_on)
        msg_direction = "O"
        channel_uuid = uuid.uuid4()
        channel_name = "Test Channel"
        cls.data = dict(
            uuid=contact_uuid,
            name=contact_name,
            msg__uuid=msg_uuid,
            msg__text=msg_text,
            msg__sent_on=msg_sent_on,
            msg__direction=msg_direction,
            channel__uuid=channel_uuid,
            channel__name=channel_name,
        )
        cls.message = pb2.ActiveContactDetail(
            uuid=str(contact_uuid),
            name=contact_name,
            msg=pb2.Msg(
                uuid=str(msg_uuid),
                text=msg_text,
                sent_on=ts,
                direction=pb2.OUTPUT,
            ),
            channel=pb2.Channel(uuid=str(channel_uuid), name=channel_name),
        )

    def test_serialize(self):
        serializer = self.serializer_class(self.data)
        self.assertEqual(serializer.message, self.message)


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

        return pb2.BillingRequest(org_uuid=str(org_uuid), before=before_message, after=after_message)

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
        cls.valid_message = pb2.BillingRequest(org_uuid=str(org_uuid), before=before_message, after=after_message)

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
            self.assertIsInstance(serializer.message, pb2.BillingRequest)

        with self.assertRaisesRegex(KeyError, "before"):
            serializer = BillingRequestSerializer(dict(org_uuid="dontmatternow", after=tz.now()))
            self.assertIsInstance(serializer.message, pb2.BillingRequest)

        with self.assertRaisesRegex(KeyError, "after"):
            serializer = BillingRequestSerializer(dict(org_uuid="dontmatternow", before=tz.now()))
            self.assertIsInstance(serializer.message, pb2.BillingRequest)

    def test_required(self):
        serializer = BillingRequestSerializer(message=pb2.BillingRequest())
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
        self.assertEqual(
            serializer.errors["org_uuid"][0],
            ErrorDetail(string="Must be a valid UUID.", code="invalid"),
        )

    def test_invalid_after(self):
        msg = self.create_message(
            after=tz.now() + tz.timedelta(hours=1),
            before=tz.now() + tz.timedelta(hours=2),
        )
        serializer = self.serializer_class(message=msg)
        self.assertFalse(serializer.is_valid())
        self.assertNotIn("before", serializer.errors)
        self.assertNotIn("org_uuid", serializer.errors)
        self.assertIn("after", serializer.errors)
        self.assertEqual(len(serializer.errors["after"]), 1)
        self.assertEqual(
            serializer.errors["after"][0],
            ErrorDetail(string="Cannot search after this date.", code="invalid"),
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


class BillingServiceTest(RPCTransactionTestCase):

    def setUp(self):
        super().setUp()
        self.stub = stubs.BillingStub(self.channel)

    def test_total(self):
        ...

    def test_detailed(self):
        ...
