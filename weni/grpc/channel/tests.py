import json

from django.contrib.auth import get_user_model
from django_grpc_framework.test import RPCTransactionTestCase

from temba.channels.models import Channel
from temba.orgs.models import Org, OrgRole
from temba.channels.types.weniwebchat.type import CONFIG_BASE_URL
from weni.protobuf.flows import channel_pb2, channel_pb2_grpc


User = get_user_model()


class gRPCClient:
    def channel_create_request(self, **kwargs):
        stub = channel_pb2_grpc.ChannelControllerStub(self.channel)
        return stub.Create(channel_pb2.ChannelCreateRequest(**kwargs))

    def channel_retrieve_request(self, **kwargs):
        stub = channel_pb2_grpc.ChannelControllerStub(self.channel)
        return stub.Retrieve(channel_pb2.ChannelRetrieveRequest(**kwargs))

    def channel_relesase_request(self, **kwargs):
        stub = channel_pb2_grpc.ChannelControllerStub(self.channel)
        return stub.Destroy(channel_pb2.ChannelDestroyRequest(**kwargs))


class ReleaseChannelServiceTest(gRPCClient, RPCTransactionTestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="123", email="test@weni.ai")
        self.org = Org.objects.create(
            name="Weni", timezone="Africa/Kigali", created_by=self.user, modified_by=self.user
        )

        super().setUp()

        self.channel_obj = Channel.create(self.org, self.user, None, "WWC", "Teste WWC")

    def test_released_channel_is_active_equal_to_false(self):
        self.channel_relesase_request(uuid=self.channel_obj.uuid, user=self.user.email)
        self.assertFalse(Channel.objects.get(id=self.channel_obj.id).is_active)


class CreateChannelServiceTest(gRPCClient, RPCTransactionTestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="fake@weni.ai", password="123", email="fake@weni.ai")
        self.org = Org.objects.create(
            name="Weni", timezone="America/Sao_Paulo", created_by=self.user, modified_by=self.user
        )
        self.org.add_user(self.user, OrgRole.ADMINISTRATOR)

        super().setUp()

    def test_create_weni_web_chat_channel(self):

        data = json.dumps({"name": "test", "base_url": "https://weni.ai"})

        response = self.channel_create_request(
            user=self.user.email, org=str(self.org.uuid), data=data, channeltype_code="WWC"
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
            name="Weni", timezone="America/Sao_Paulo", created_by=self.user, modified_by=self.user
        )

        super().setUp()

        self.channel_obj = Channel.create(self.org, self.user, None, "WWC", "Teste WWC", "test", {"fake_key": "fake_value"})

    def test_channel_retrieve_returned_fields(self):
        response = self.channel_retrieve_request(uuid=str(self.channel_obj.uuid))
        self.assertEqual(response.name, self.channel_obj.name)
        self.assertEqual(response.address, self.channel_obj.address)
        self.assertEqual(json.loads(response.config), self.channel_obj.config)
