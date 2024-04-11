from django.db import models
from temba.event_driven.publisher.rabbitmq_publisher import RabbitmqPublisher


def create_recent_activity(instance: models.Model, created: bool, delete=None):
    if instance.is_active:
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
