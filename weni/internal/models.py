from uuid import uuid4

from django.db import models

from temba.tickets.models import Ticketer, Topic
from temba.orgs.models import Org


class TicketerQueue(Topic):
    topic = models.OneToOneField(
        Topic, on_delete=models.CASCADE, parent_link=True, related_name="queue"
    )
    ticketer = models.ForeignKey(
        Ticketer, on_delete=models.CASCADE, related_name="queues"
    )

    class Meta:
        db_table = "internal_tickets_ticketerqueue"

    def __str__(self):
        return f"Queue[uuid={self.uuid}, name={self.name}]"

    def release(self):
        self.is_active = False
        self.save()


class Project(Org):
    project_uuid = models.UUIDField(default=uuid4, unique=True)

    class Meta:
        db_table = "internal_project"

    def __str__(self):
        return f"Project[uuid={self.project_uuid}, org={self.org}]"

    @property
    def org(self):
        return self.org_ptr
