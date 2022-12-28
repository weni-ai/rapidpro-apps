import celery
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from temba.channels.models import Channel
from temba.flows.models import Flow
from temba.triggers.models import Trigger
from temba.campaigns.models import Campaign


def create_recent_activity(instance: models.Model, created: bool):
    if instance.is_active:
        action = "CREATE" if created else "UPDATE"

        celery.execute.send_task("create_recent_activity", kwargs=dict(
            action=action,
            entity=instance.__class__.__name__.upper(),
            entity_name=getattr(instance, "name", None),
            user=instance.modified_by.email,
            flow_organization=str(instance.org.uuid),
        ))


@receiver(post_save, sender=Channel)
def channel_recent_activity_signal(sender, instance: Channel, created: bool, **kwargs):
    create_recent_activity(instance, created)


@receiver(post_save, sender=Flow)
def flow_recent_activity_signal(sender, instance: Flow, created: bool, **kwargs):
    update_fields = kwargs.get("update_fields")
    if update_fields != frozenset({
        'version_number',
        'modified_on',
        'saved_on',
        'modified_by',
        'metadata',
        'saved_by',
        'base_language',
        'has_issues'
    }):
        # This condition prevents two events from being sent when creating a flow
        create_recent_activity(instance, created)


@receiver(post_save, sender=Trigger)
def trigger_recent_activity_signal(sender, instance: Trigger, created: bool, **kwargs):
    create_recent_activity(instance, created)


@receiver(post_save, sender=Campaign)
def campaign_recent_activity_signal(sender, instance: Campaign, created: bool, **kwargs):
    create_recent_activity(instance, created)
