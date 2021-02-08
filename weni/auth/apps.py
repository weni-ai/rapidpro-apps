from django.apps import AppConfig

from .urls import urlpatterns
from ..utils.app_config import update_urlpatterns


class AuthConfig(AppConfig):
    name = "weni.auth"

    def ready(self):
        update_urlpatterns(urlpatterns)
