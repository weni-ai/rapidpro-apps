from django.db import models

from temba.tickets.models import Ticketer, Topic


class TicketerQueue(Topic):
    topic = models.OneToOneField(Topic, on_delete=models.CASCADE, parent_link=True, related_name="queue")
    ticketer = models.ForeignKey(Ticketer, on_delete=models.CASCADE, related_name="queues")

    class Meta:
        db_table = "internal_tickets_ticketerqueue"

    def __str__(self):
        return f"Queue[uuid={self.uuid}, name={self.name}]"
