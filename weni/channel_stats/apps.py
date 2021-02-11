from django.apps import AppConfig


class ChannelStatsConfig(AppConfig):
    name = "weni.channel_stats"

    def ready(self):
        from .urls import urlpatterns
        from ..utils.app_config import update_urlpatterns

        update_urlpatterns(urlpatterns)
