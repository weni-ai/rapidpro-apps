from django.apps import AppConfig


class TemplateMessageConfig(AppConfig):
    name = "weni.template_message"

    def ready(self):
        from weni.template_message.urls import urlpatterns
        from weni.utils.app_config import update_urlpatterns

        update_urlpatterns(urlpatterns)
