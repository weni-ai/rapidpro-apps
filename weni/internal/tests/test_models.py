from uuid import uuid4

from temba.tests import TembaTest
from temba.tickets.models import Ticketer, Topic
from temba.tickets.types.rocketchat import RocketChatType
from weni.internal.models import TicketerQueue


class TicketerQueueTestCase(TembaTest):
    def setUp(self):
        self.fake_chats_uuid = uuid4()

        super().setUp()
        self.ticketer = Ticketer.create(self.org, self.user, RocketChatType.slug, "Email (bob@acme.com)", {})
        self.queue = TicketerQueue.objects.create(
            created_by=self.user,
            modified_by=self.user,
            org=self.org,
            name="Fake Name",
            uuid=self.fake_chats_uuid,
            ticketer=self.ticketer,
        )

    def test_when_creating_queue_a_topic_is_created(self):
        self.assertTrue(Topic.objects.filter(queue=self.queue).exists())

    def test_if_topic_name_is_the_same_as_queue(self):
        topic = Topic.objects.get(queue=self.queue)
        self.assertEquals(topic.name, self.queue.name)

    def test_changing_queue_name_also_changes_the_topic_name(self):
        self.queue.name = "Fake Name 2"
        self.queue.save()

        topic = Topic.objects.get(queue=self.queue)
        self.assertEquals(topic.name, self.queue.name)
