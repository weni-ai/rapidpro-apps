from django.conf import settings
from weni.internal.clients.authenticators import InternalAuthenticator


class BaseInternalClient(object):
    def __init__(self, base_url: str = None, authenticator: InternalAuthenticator = None):
        self.base_url = base_url if base_url else settings.CONNECT_BASE_URL
        self.authenticator = authenticator if authenticator else InternalAuthenticator()

    def get_url(self, endpoint: str) -> str:
        return f"{self.base_url}{endpoint}"
