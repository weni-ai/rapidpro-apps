from django.apps import AppConfig


class TicketerQueuesConfig(AppConfig):
    name = "weni.ticketer_queues"

    def ready(self):
        from weni.ticketer_queues.urls import urlpatterns
        from weni.utils.app_config import update_urlpatterns

        update_urlpatterns(urlpatterns)
