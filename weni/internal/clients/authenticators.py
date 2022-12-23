import requests
from django.conf import settings


class InternalAuthenticator(object):
    def _get_module_token(self):
        response = requests.post(
            url=settings.OIDC_OP_TOKEN_ENDPOINT,
            data={
                "client_id": settings.OIDC_RP_CLIENT_ID,
                "client_secret": settings.OIDC_RP_CLIENT_SECRET,
                "grant_type": "client_credentials",
            },
        )

        token = response.json().get("access_token")
        return f"Bearer {token}"
    
    @property
    def headers(self):
        return {
            "Content-Type": "application/json; charset: utf-8",
            "Authorization": self._get_module_token(),
        }
