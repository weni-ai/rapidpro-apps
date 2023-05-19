import json
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django_grpc_framework.test import RPCTransactionTestCase
from rest_framework import serializers

from temba.channels.models import Channel
from temba.orgs.models import Org, OrgRole
from weni.protobuf.flows import channel_pb2, channel_pb2_grpc


User = get_user_model()


class gRPCClient:
    def channel_create_whatsapp_cloud_request(self, **kwargs):
        stub = channel_pb2_grpc.ChannelControllerStub(self.channel)
        return stub.CreateWAC(channel_pb2.ChannelWACCreateRequest(**kwargs))

    def channel_create_request(self, **kwargs):
        stub = channel_pb2_grpc.ChannelControllerStub(self.channel)
        return stub.Create(channel_pb2.ChannelCreateRequest(**kwargs))

    def channel_retrieve_request(self, **kwargs):
        stub = channel_pb2_grpc.ChannelControllerStub(self.channel)
        return stub.Retrieve(channel_pb2.ChannelRetrieveRequest(**kwargs))

    def channel_relesase_request(self, **kwargs):
        stub = channel_pb2_grpc.ChannelControllerStub(self.channel)
        return stub.Destroy(channel_pb2.ChannelDestroyRequest(**kwargs))

    def channel_list_request(self, **kwargs):
        stub = channel_pb2_grpc.ChannelControllerStub(self.channel)
        return stub.List(channel_pb2.ChannelListRequest(**kwargs))


class ReleaseChannelServiceTest(gRPCClient, RPCTransactionTestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="123", email="test@weni.ai")
        self.org = Org.objects.create(
            name="Weni",
            timezone="Africa/Kigali",
            created_by=self.user,
            modified_by=self.user,
        )

        super().setUp()

        self.channel_obj = Channel.create(self.org, self.user, None, "WWC", "Test WWC")

    def test_released_channel_is_active_equal_to_false(self):
        self.channel_relesase_request(uuid=self.channel_obj.uuid, user=self.user.email)
        self.assertFalse(Channel.objects.get(id=self.channel_obj.id).is_active)


class CreateWACServiceTest(gRPCClient, RPCTransactionTestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="fake@weni.ai", password="123", email="fake@weni.ai")
        self.org = Org.objects.create(
            name="Weni",
            timezone="America/Sao_Paulo",
            created_by=self.user,
            modified_by=self.user,
        )
        self.org.add_user(self.user, OrgRole.ADMINISTRATOR)

        self.config = {
            "wa_number": "5561995743921",
            "wa_verified_name": "Weni Test",
            "wa_waba_id": "2433443436435435",
            "wa_currency": "USD",
            "wa_business_id": "3443243234254322",
            "wa_message_template_namespace": "6b186dea_ds6d_44s2_b9xd_de87a12212e5",
        }

        super().setUp()

    @patch("temba.channels.types.whatsapp_cloud.type.WhatsAppCloudType.activate")
    def test_create_whatsapp_cloud_channel(self, mock):
        mock.return_value = None

        phone_number_id = "5426423432"

        channel = self.channel_create_whatsapp_cloud_request(
            org=str(self.org.uuid),
            user=self.user.email,
            phone_number_id=phone_number_id,
            config=json.dumps(self.config),
        )

        self.assertTrue(hasattr(channel, "uuid"))
        self.assertEqual(channel.name, self.config.get("wa_verified_name"))
        self.assertEqual(json.loads(channel.config), self.config)
        self.assertEqual(channel.address, phone_number_id)

    @patch("temba.channels.types.whatsapp_cloud.type.WhatsAppCloudType.activate")
    def test_create_whatsapp_cloud_channel_invalid_address(self, mock):
        mock.return_value = None

        phone_number_id = "5426423432"

        self.channel_create_whatsapp_cloud_request(
            org=str(self.org.uuid),
            user=self.user.email,
            phone_number_id=phone_number_id,
            config=json.dumps(self.config),
        )

        with self.assertRaises(serializers.ValidationError):
            self.channel_create_whatsapp_cloud_request(
                org=str(self.org.uuid),
                user=self.user.email,
                phone_number_id=phone_number_id,
                config=json.dumps(self.config),
            )


class CreateChannelServiceTest(gRPCClient, RPCTransactionTestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="fake@weni.ai", password="123", email="fake@weni.ai")
        self.org = Org.objects.create(
            name="Weni",
            timezone="America/Sao_Paulo",
            created_by=self.user,
            modified_by=self.user,
        )
        self.org.add_user(self.user, OrgRole.ADMINISTRATOR)

        super().setUp()

    def test_create_weni_web_chat_channel(self):
        data = json.dumps({"name": "test", "base_url": "https://weni.ai"})

        response = self.channel_create_request(
            user=self.user.email,
            org=str(self.org.uuid),
            data=data,
            channeltype_code="WWC",
        )
        channel = Channel.objects.get(uuid=response.uuid)
        self.assertEqual(channel.address, response.address)
        self.assertEqual(channel.name, response.name)
        self.assertEqual(channel.config.get("base_url"), "https://weni.ai")
        self.assertEqual(channel.org, self.org)
        self.assertEqual(channel.created_by, self.user)
        self.assertEqual(channel.modified_by, self.user)
        self.assertEqual(channel.channel_type, "WWC")


class RetrieveChannelServiceTest(gRPCClient, RPCTransactionTestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="fake@weni.ai", password="123", email="fake@weni.ai")
        self.org = Org.objects.create(
            name="Weni",
            timezone="America/Sao_Paulo",
            created_by=self.user,
            modified_by=self.user,
        )

        super().setUp()

        self.channel_obj = Channel.create(
            self.org,
            self.user,
            None,
            "WWC",
            "Test WWC",
            "test",
            {"fake_key": "fake_value"},
        )

    def test_channel_retrieve_returned_fields(self):
        response = self.channel_retrieve_request(uuid=str(self.channel_obj.uuid))
        self.assertEqual(response.name, self.channel_obj.name)
        self.assertEqual(response.address, self.channel_obj.address)
        self.assertEqual(json.loads(response.config), self.channel_obj.config)


class ListChannelServiceTest(gRPCClient, RPCTransactionTestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="fake@weni.ai", password="123", email="fake@weni.ai")
        self.orgs = [
            Org.objects.create(
                name=f"Org {org}",
                timezone="America/Sao_Paulo",
                created_by=self.user,
                modified_by=self.user,
            )
            for org in range(2)
        ]

        for channel in range(6):
            Channel.create(
                self.orgs[0] if channel % 2 == 0 else self.orgs[1],
                self.user,
                None,
                "WWC" if channel % 2 == 0 else "VK",
                f"Test {channel}",
                "test",
                {},
            )

        super().setUp()

    def test_list_all_channels(self):
        response = list(self.channel_list_request())
        self.assertEqual(len(response), 6)

    def test_list_channels_filtered_by_type(self):
        response = list(self.channel_list_request(channel_type="WWC"))
        self.assertEqual(len(response), 3)

    def test_list_channels_filtered_by_org_uuid(self):
        org_uuid = str(self.orgs[0].uuid)
        response = list(self.channel_list_request(org=org_uuid))
        self.assertEqual(len(response), 3)

        channel = Channel.objects.get(uuid=response[0].uuid)
        self.assertEqual(channel.org, self.orgs[0])
