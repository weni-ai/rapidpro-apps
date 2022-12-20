from temba.temba_celery import app as celery_app

from weni.internal.clients import ConnectInternalClient


@celery_app.task(name="create_recent_activity")
def create_recent_activity(action: str, entity: str, entity_name: str, user: str, flow_organization: str):
    client = ConnectInternalClient()
    client.create_recent_activiry(action, entity, entity_name, user, flow_organization)
