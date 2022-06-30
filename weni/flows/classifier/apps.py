from django.apps import AppConfig


class AnalyticsApiConfig(AppConfig):
    name = "weni.flows.classifier"

    def ready(self):
        from .urls import urlpatterns
        from ...utils.app_config import update_urlpatterns

        update_urlpatterns(urlpatterns)
