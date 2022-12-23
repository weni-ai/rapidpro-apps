from celery import shared_task

from weni.internal.clients import ConnectInternalClient


@shared_task(name="create_recent_activity")
def create_recent_activity(action: str, entity: str, entity_name: str, user: str, flow_organization: str):
    client = ConnectInternalClient()
    client.create_recent_activity(action, entity, entity_name, user, flow_organization)
