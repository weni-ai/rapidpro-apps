from django.contrib.auth import get_user_model
from django_grpc_framework.test import RPCTransactionTestCase

from temba.channels.models import Channel
from temba.channels.types.weniwebchat.type import CONFIG_BASE_URL
from weni.grpc.channel.grpc_gen import channel_pb2, channel_pb2_grpc


User = get_user_model()


class WeniWebChatCreateServiceTest(RPCTransactionTestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="123", email="test@weni.ai")

        super().setUp()
        self.stub = channel_pb2_grpc.WeniWebChatControllerStub(self.channel)

    def test_create_weni_web_chat_channel(self):
        request_data = dict(name="fake wwc", user=self.user.email, base_url="https://dash.weni.ai")
        response = self.channel_create_request(**request_data)

        channel = Channel.objects.get(name=response.name)
        self.assertEqual(channel.created_by, self.user)
        self.assertEqual(channel.config[CONFIG_BASE_URL], request_data["base_url"])

    def channel_create_request(self, **kwargs):
        return self.stub.Create(channel_pb2.WeniWebChatCreateRequest(**kwargs))
