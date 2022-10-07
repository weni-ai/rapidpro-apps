from django.utils.http import urlencode
from django.urls import reverse
from uuid import uuid4
from abc import ABC
from django.contrib.auth.models import Group

from temba.tests import TembaTest
from temba.tickets.models import Ticketer, Topic
from weni.internal.models import TicketerQueue
from temba.tickets.types.mailgun.type import MailgunType
from temba.api.models import APIToken


class RequestMixin(ABC):
    def get_response(self, **query_params):
        url = "%s.json?%s" % (
            reverse("api.v2.ticketer_queues"),
            urlencode(query_params),
        )

        token = APIToken.get_or_create(self.org, self.admin, Group.objects.get(name="Administrators"))

        return self.client.get(
            url,
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Token {token.key}",
        )


class TicketerQueuesTest(TembaTest, RequestMixin):
    def setUp(self):
        self.fake_chats_uuid = uuid4()

        super().setUp()
        self.ticketer = Ticketer.create(self.org, self.user, MailgunType.slug, "Email (bob@acme.com)", {})
        self.queue = TicketerQueue.objects.create(
            created_by=self.user,
            modified_by=self.user,
            org=self.org,
            name="Fake Name",
            uuid=self.fake_chats_uuid,
            ticketer=self.ticketer,
        )

    def test_ticketer_queues_endpoint(self):
        response = self.get_response(ticketer_uuid=self.ticketer.uuid)
        topic = Topic.objects.get(queue=self.queue)
        self.assertEqual(topic.name, response.json()[0]["name"])
