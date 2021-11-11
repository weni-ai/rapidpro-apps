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
        stub = channel_pb2_grpc.WeniWebChatControllerStub(self.channel)
        return stub.Create(channel_pb2.WeniWebChatCreateRequest(**kwargs))

    def channel_relesase_request(self, **kwargs):
        stub = channel_pb2_grpc.ChannelControllerStub(self.channel)
        return stub.Destroy(channel_pb2.ChannelDestroyRequest(**kwargs))


class WeniWebChatCreateServiceTest(gRPCClient, RPCTransactionTestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="123", email="test@weni.ai")
        self.org = Org.objects.create(
            name="Weni", timezone="Africa/Kigali", created_by=self.user, modified_by=self.user
        )

        super().setUp()
        self.stub = channel_pb2_grpc.WeniWebChatControllerStub(self.channel)

    def test_create_weni_web_chat_channel(self):
        request_data = dict(
            org=str(self.org.uuid), name="fake wwc", user=self.user.email, base_url="https://dash.weni.ai"
        )
        response = self.channel_create_request(**request_data)

        channel = Channel.objects.get(uuid=response.uuid)
        self.assertEqual(channel.created_by, self.user)
        self.assertEqual(channel.config[CONFIG_BASE_URL], request_data["base_url"])


class ReleaseChannelServiceTest(gRPCClient, RPCTransactionTestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="123", email="test@weni.ai")
        self.org = Org.objects.create(
            name="Weni", timezone="Africa/Kigali", created_by=self.user, modified_by=self.user
        )

        super().setUp()

        response = self.channel_create_request(
            org=str(self.org.uuid), name="fake wwc", user=self.user.email, base_url="https://dash.weni.ai"
        )
        self.channel_obj = Channel.objects.get(uuid=response.uuid)

    def test_alg(self):
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
        self.assertEqual(channel.name, "test")
        self.assertEqual(channel.config.get("base_url"), "https://weni.ai")
        self.assertEqual(channel.org, self.org)
        self.assertEqual(channel.created_by, self.user)
        self.assertEqual(channel.modified_by, self.user)
        self.assertEqual(channel.channel_type, "WWC")

    def channel_create_request(self, **kwargs):
        stub = channel_pb2_grpc.ChannelControllerStub(self.channel)
        return stub.Create(channel_pb2.ChannelCreateRequest(**kwargs))
