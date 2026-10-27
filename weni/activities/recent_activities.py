import logging

from django.conf import settings
from django.db import models
from temba.event_driven.publisher.rabbitmq_publisher import RabbitmqPublisher

from weni_commons.change_history import Action

from weni.activities.change_history import notify_change_history

logger = logging.getLogger(__name__)


def _publish_legacy_recent_activity(instance: models.Model, created: bool, delete=None):
    rabbitmq_publisher = RabbitmqPublisher()
    if delete:
        action = "DELETE"
        rabbitmq_publisher.send_message(
            body=dict(
                action=action,
                entity=instance.__class__.__name__.upper(),
                entity_name=getattr(instance, "name", None),
                entity_uuid=str(instance.uuid),
                project_uuid=str(instance.org.project.project_uuid),
                user=instance.modified_by.email,
                flow_organization=str(instance.org.uuid),
            ),
            exchange="recent-activities.topic",
            routing_key="flow-delete",
        )
    else:
        action = "CREATE" if created else "UPDATE"
        rabbitmq_publisher.send_message(
            body=dict(
                action=action,
                entity=instance.__class__.__name__.upper(),
                entity_name=getattr(instance, "name", None),
                project_uuid=str(instance.org.project.project_uuid),
                user=instance.modified_by.email,
                flow_organization=str(instance.org.uuid),
            ),
            exchange="recent-activities.topic",
            routing_key="",
        )


def _publish_change_history(instance: models.Model, created: bool, delete=None, action: Action = None):
    if not getattr(settings, "CHANGE_HISTORY_ENABLED", True):
        return

    try:
        # objects released together with their org are not part of the project history
        if not instance.org.is_active:
            return

        notify_change_history(instance, created, delete=bool(delete), action=action)
    except Exception:
        logger.exception("Failed to publish change history for %s", instance)


def create_recent_activity(
    instance: models.Model, created: bool, delete=None, change_history_action: Action = None
):
    if not instance.is_active:
        return

    if getattr(settings, "RECENT_ACTIVITIES_LEGACY_ENABLED", True):
        try:
            _publish_legacy_recent_activity(instance, created, delete)
        except Exception:
            logger.exception("Failed to publish legacy recent activity for %s", instance)

    # an active instance flagged as deleted is an archive (Flow.archive): it can still be
    # restored, and its post_save already published the Change History DEACTIVATE
    if not delete:
        _publish_change_history(instance, created, action=change_history_action)


def create_change_history_activity(instance: models.Model, created: bool, delete: bool = False):
    if not instance.is_active and not delete:
        return

    _publish_change_history(instance, created, delete)
