import requests

from weni.internal.clients.base import BaseInternalClient
from weni.internal.models import Project


class ConnectInternalClient(BaseInternalClient):
    def create_recent_activity(
        self,
        action: str,
        entity: str,
        entity_name: str,
        user: str,
        flow_organization: str,
    ):
        body = dict(
            action=action,
            entity=entity,
            entity_name=entity_name,
            user=user,
            flow_organization=flow_organization,
        )
        response = requests.post(
            self.get_url("/v1/recent-activity"),
            headers=self.authenticator.headers,
            json=body,
        )

        return response

    def update_project(self, project: Project):
        body = dict(
            flow_organization=str(project.uuid),
            flow_id=project.id,
        )
        response = requests.patch(
            self.get_url(f"/v2/internals/connect/projects/{project.project_uuid}"),
            headers=self.authenticator.headers,
            json=body,
        )

        return response
