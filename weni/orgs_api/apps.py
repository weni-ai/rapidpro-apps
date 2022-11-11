from django.apps import AppConfig


class OrgApiConfig(AppConfig):
    name = "weni.orgs_api"

    def ready(self):
        from .urls import urlpatterns
        from ..utils.app_config import update_urlpatterns

        update_urlpatterns(urlpatterns)
