import requests

from weni.internal.clients.base import BaseInternalClient


class ConnectInternalClient(BaseInternalClient):

    def create_recent_activity(self, action: str, entity: str, entity_name: str, user: str, flow_organization: str):
        body = dict(
            action=action,
            entity=entity,
            entity_name=entity_name,
            user=user,
            flow_organization=flow_organization,
        )
        response = requests.post(self.get_url("/v1/recent-activity"), headers=self.authenticator.headers, json=body)

        return response
