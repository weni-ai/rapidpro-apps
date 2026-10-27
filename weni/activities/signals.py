from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from temba.channels.models import Channel
from temba.flows.models import Flow
from temba.triggers.models import Trigger
from temba.campaigns.models import Campaign
from weni_commons.change_history import Action

from weni.activities.change_history import PREVIOUS_NAME_ATTR
from weni.activities.recent_activities import create_change_history_activity, create_recent_activity

FLOW_REVISION_UPDATE_FIELDS = frozenset(
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
)

ARCHIVE_UPDATE_FIELDS = frozenset({"is_archived", "modified_by", "modified_on"})


def _is_release(instance, update_fields) -> bool:
    return update_fields is not None and "is_active" in update_fields and not instance.is_active


def _archive_action(instance) -> Action:
    return Action.DEACTIVATE if instance.is_archived else Action.ACTIVATE


@receiver(pre_save, sender=Flow)
@receiver(pre_save, sender=Channel)
@receiver(pre_save, sender=Campaign)
def remember_previous_name(sender, instance, update_fields=None, **kwargs):
    # the same instance can be saved more than once, so never keep a name from an earlier save
    instance.__dict__.pop(PREVIOUS_NAME_ATTR, None)

    if instance._state.adding or instance.pk is None:
        return
    if update_fields is not None and "name" not in update_fields:
        return
    if getattr(instance, "is_system", False):
        return

    previous = sender._base_manager.filter(pk=instance.pk).values_list("name", flat=True).first()
    setattr(instance, PREVIOUS_NAME_ATTR, previous)


@receiver(post_save, sender=Channel)
def channel_recent_activity_signal(sender, instance: Channel, created: bool, **kwargs):
    update_fields = kwargs.get("update_fields")
    if _is_release(instance, update_fields):
        create_change_history_activity(instance, created=False, delete=True)
    elif instance.channel_type not in ["WA", "WAC", "TM"] or update_fields != frozenset(
        {
            "config",
        },
    ):
        create_recent_activity(instance, created)


@receiver(post_save, sender=Flow)
def flow_recent_activity_signal(sender, instance: Flow, created: bool, **kwargs):
    update_fields = kwargs.get("update_fields")
    if _is_release(instance, update_fields):
        # system flows (campaign message events) are released along with their event
        if not instance.is_system:
            create_change_history_activity(instance, created=False, delete=True)
    elif update_fields == ARCHIVE_UPDATE_FIELDS:
        create_recent_activity(instance, created, change_history_action=_archive_action(instance))
    elif update_fields != FLOW_REVISION_UPDATE_FIELDS:
        create_recent_activity(instance, created)
    elif instance.revisions.exists():
        # Editor saves; the first revision is skipped because it belongs to the flow creation
        create_change_history_activity(instance, created=False)


@receiver(post_save, sender=Trigger)
def trigger_recent_activity_signal(sender, instance: Trigger, created: bool, **kwargs):
    update_fields = kwargs.get("update_fields")
    if _is_release(instance, update_fields):
        create_change_history_activity(instance, created=False, delete=True)
    elif update_fields == ARCHIVE_UPDATE_FIELDS:
        create_recent_activity(instance, created, change_history_action=_archive_action(instance))
    else:
        create_recent_activity(instance, created)


@receiver(post_save, sender=Campaign)
def campaign_recent_activity_signal(
    sender, instance: Campaign, created: bool, **kwargs
):
    create_recent_activity(instance, created)
