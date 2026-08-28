from django.utils import timezone

from weni_commons.change_history import Action, Entity, Module, Notifier

ENTITIES = {
    "FLOW": Entity.FLOW,
    "CHANNEL": Entity.CHANNEL,
    "TRIGGER": Entity.TRIGGER,
    "CAMPAIGN": Entity.CAMPAIGN,
}


def notify_change_history(instance, created: bool, delete: bool = False):
    entity = ENTITIES.get(instance.__class__.__name__.upper())
    if entity is None:
        return

    if delete:
        action = Action.DELETE
    else:
        action = Action.CREATE if created else Action.UPDATE

    Notifier.notify_change(
        project_uuid=str(instance.org.project.project_uuid),
        user_email=instance.modified_by.email,
        date=getattr(instance, "modified_on", None) or timezone.now(),
        action=action,
        entity=entity,
        module=Module.FLOWS,
        object_id=str(instance.uuid),
        object_name=getattr(instance, "name", None),
    )
