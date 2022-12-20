from django.db import models
from django.contrib.auth.models import User

from temba.tickets.models import Ticketer, Topic
from temba.orgs.models import Org


class TicketerQueue(Topic):
    topic = models.OneToOneField(Topic, on_delete=models.CASCADE, parent_link=True, related_name="queue")
    ticketer = models.ForeignKey(Ticketer, on_delete=models.CASCADE, related_name="queues")

    class Meta:
        db_table = "internal_tickets_ticketerqueue"

    def __str__(self):
        return f"Queue[uuid={self.uuid}, name={self.name}]"


class RecentActivity(models.Model):
    UPDATE = "UPDATE"
    CREATE = "CREATE"

    ACTIONS_CHOICES = (
        (CREATE, "Entity Created"),
        (UPDATE, "Updated Entity")
    )

    FLOW = "FLOW"
    CHANNEL = "CHANNEL"
    TRIGGER = "TRIGGER"
    CAMPAIGN = "CAMPAIGN"

    ENTITY_CHOICES = (
        (FLOW, "Flow Entity"),
        (CHANNEL, "Chanell Entity"),
        (TRIGGER, "Trigger Entity"),
        (CAMPAIGN, "Campaign Entity")
    )

    org = models.ForeignKey(Org, on_delete=models.PROTECT)
    action = models.CharField(max_length=6, choices=ACTIONS_CHOICES)
    entity = models.CharField(max_length=8, choices=ENTITY_CHOICES)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    entity_name = models.CharField(max_length=255, null=True)
    created_on = models.DateTimeField()

    class Meta:
        db_table = "internal_activities_recentactivity"


    def __str__(self) -> str:
        return f"""{self.org} - {self.entity} - {self.entity_name} -
                   {self.action} - {self.user} - {str(self.created_on)}"""
