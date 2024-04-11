from django.db.models.signals import post_save
from django.dispatch import receiver

from temba.channels.models import Channel
from temba.flows.models import Flow
from temba.triggers.models import Trigger
from temba.campaigns.models import Campaign

from weni.activities.recent_activities import create_recent_activity


@receiver(post_save, sender=Channel)
def channel_recent_activity_signal(sender, instance: Channel, created: bool, **kwargs):
    update_fields = kwargs.get("update_fields")
    if instance.channel_type not in ["WA", "WAC"] or update_fields != frozenset(
        {
            "config",
        },
    ):
        create_recent_activity(instance, created)


@receiver(post_save, sender=Flow)
def flow_recent_activity_signal(sender, instance: Flow, created: bool, **kwargs):
    update_fields = kwargs.get("update_fields")
    if update_fields != frozenset(
        {
            "version_number",
            "modified_on",
            "saved_on",
            "modified_by",
            "metadata",
            "saved_by",
            "base_language",
            "has_issues",
        }
    ):
        # This condition prevents two events from being sent when creating a flow
        create_recent_activity(instance, created)


@receiver(post_save, sender=Trigger)
def trigger_recent_activity_signal(sender, instance: Trigger, created: bool, **kwargs):
    create_recent_activity(instance, created)


@receiver(post_save, sender=Campaign)
def campaign_recent_activity_signal(
    sender, instance: Campaign, created: bool, **kwargs
):
    create_recent_activity(instance, created)
