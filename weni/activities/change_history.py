from django.utils import timezone

from weni_commons.change_history import Action, Entity, Module, Notifier

ENTITIES = {
    "FLOW": Entity.FLOW,
    "CHANNEL": Entity.CHANNEL,
    "TRIGGER": Entity.TRIGGER,
    "CAMPAIGN": Entity.CAMPAIGN,
}

PREVIOUS_NAME_ATTR = "_change_history_previous_name"


def _name_change(instance):
    # read from __dict__ so only the value stored by the pre_save receiver counts
    previous = instance.__dict__.pop(PREVIOUS_NAME_ATTR, None)
    current = getattr(instance, "name", None)
    if previous is None or previous == current:
        return None, None
    return previous, current


def notify_change_history(instance, created: bool, delete: bool = False):
    entity = ENTITIES.get(instance.__class__.__name__.upper())
    if entity is None:
        return

    if delete:
        action = Action.DELETE
    else:
        action = Action.CREATE if created else Action.UPDATE

    old_value, new_value = _name_change(instance)

    Notifier.notify_change(
        project_uuid=str(instance.org.project.project_uuid),
        user_email=instance.modified_by.email,
        date=getattr(instance, "modified_on", None) or timezone.now(),
        action=action,
        entity=entity,
        module=Module.FLOWS,
        object_id=str(getattr(instance, "uuid", None) or instance.pk),
        object_name=getattr(instance, "name", None),
        old_value=old_value,
        new_value=new_value,
    )
