from django.apps import AppConfig


class FlowChannelApiConfig(AppConfig):
    name = "weni.flows.channel"

    def ready(self):
        from .urls import urlpatterns
        from ...utils.app_config import update_urlpatterns

        update_urlpatterns(urlpatterns)