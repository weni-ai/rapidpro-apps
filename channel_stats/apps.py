from django.apps import AppConfig


class ChannelStatsConfig(AppConfig):
    name = 'apps.channel_stats'

    def ready(self):
        from temba.api.v2.urls import urlpatterns

        from .urls import urlpatterns as app_urls

        urlpatterns.extend(app_urls)
