import json
from uuid import uuid4

from django.urls import reverse
from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework.permissions import AllowAny
from rest_framework import status

from temba.tests import TembaTest
from temba.tickets.models import Ticketer
from temba.tickets.types.rocketchat import RocketChatType
from weni.internal.tickets import views
from weni.internal.models import TicketerQueue


class TicketerQueueViewTestMixin(object):
    action: dict

    def setUp(self):
        self.fake_chats_uuid = uuid4()
        self.factory = APIRequestFactory()
        self.view = views.TicketerQueueViewSet
        self.view.permission_classes = [AllowAny]

        super().setUp()

        self.ticketer = Ticketer.create(self.org, self.user, RocketChatType.slug, "Email (bob@acme.com)", {})
        self.ticketer.config = {"sector_uuid": str(self.ticketer.uuid)}
        self.ticketer.save(update_fields=("config",))
        self.queue = TicketerQueue.objects.create(
            created_by=self.user,
            modified_by=self.user,
            org=self.org,
            name="Fake Name",
            uuid=self.fake_chats_uuid,
            ticketer=self.ticketer,
        )

    def _get_response(self, request, **kwargs):
        response = self.view.as_view(self.action)(request, **kwargs)
        setattr(response, "json", json.loads(json.dumps(response.data)))
        return response

    def request(self, method: str, *args, data: dict = None, **kwargs):
        request = getattr(self.factory, method)(*args, data=data)
        force_authenticate(request, self.user)

        return self._get_response(request, **kwargs)


class CreateTicketerQueueViewTestCase(TicketerQueueViewTestMixin, TembaTest):
    action = dict(post="create")

    def test_create_queue(self):
        uuid = str(uuid4())
        kwargs = dict(ticketer_uuid=str(self.ticketer.uuid))

        url = reverse("ticketer-queues-list", kwargs=kwargs)
        self.request(
            "post",
            url,
            data={"uuid": uuid, "name": "123", "project_uuid": str(self.org.proj_uuid)},
            **kwargs,
        )
        self.assertTrue(self.ticketer.queues.filter(queue_uuid=uuid).exists())


class UpdateTicketerQueueViewTestCase(TicketerQueueViewTestMixin, TembaTest):
    action = dict(patch="partial_update")

    def test_update_queue(self):
        kwargs = dict(ticketer_uuid=str(self.ticketer.uuid), uuid=str(self.queue.uuid))
        url = reverse("ticketer-queues-detail", kwargs=kwargs)

        old_name = self.queue.name
        new_name = "Fake Name 2"

        self.request("patch", url, data={"name": new_name}, **kwargs)
        self.queue.refresh_from_db()

        self.assertEqual(self.queue.name, new_name)
        self.assertNotEqual(self.queue.name, old_name)

    def test_update_queue_purpose(self):
        kwargs = dict(ticketer_uuid=str(self.ticketer.uuid), uuid=str(self.queue.queue_uuid))
        url = reverse("ticketer-queues-detail", kwargs=kwargs)
        purpose = "Conversations related to billing and invoices"

        self.request("patch", url, data={"queue_purpose": purpose}, **kwargs)
        self.queue.refresh_from_db()

        self.assertEqual(self.queue.queue_purpose, purpose)

    def test_create_queue_with_purpose(self):
        uuid = str(uuid4())
        kwargs = dict(ticketer_uuid=str(self.ticketer.uuid))
        purpose = "Conversations related to payment issues"

        url = reverse("ticketer-queues-list", kwargs=kwargs)
        self.request(
            "post",
            url,
            data={"uuid": uuid, "name": "Payments", "queue_purpose": purpose, "project_uuid": str(self.org.proj_uuid)},
            **kwargs,
        )

        queue = self.ticketer.queues.get(queue_uuid=uuid)
        self.assertEqual(queue.name, "Payments")
        self.assertEqual(queue.queue_purpose, purpose)


class DestroyTicketerQueueViewTestCase(TicketerQueueViewTestMixin, TembaTest):
    action = dict(delete="destroy")

    def test_destroy_queue(self):
        kwargs = dict(ticketer_uuid=str(self.ticketer.uuid), uuid=str(self.queue.uuid))

        url = reverse("ticketer-queues-detail", kwargs=kwargs)

        response = self.request("delete", url, **kwargs)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_destroy_non_existing_queue(self):
        kwargs = dict(ticketer_uuid=str(self.ticketer.uuid), uuid=str(uuid4()))

        url = reverse("ticketer-queues-detail", kwargs=kwargs)

        response = self.request("delete", url, **kwargs)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
