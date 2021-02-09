from django.apps import AppConfig


class AuthConfig(AppConfig):
    name = "weni.auth"
    label = "weni_auth"

    def ready(self):
        from .urls import urlpatterns
        from ..utils.app_config import update_urlpatterns

        update_urlpatterns(urlpatterns, "temba.urls")
