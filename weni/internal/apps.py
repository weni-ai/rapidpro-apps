from django.apps import AppConfig


class InternalConfig(AppConfig):
    name = "weni.internal"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self):
        from weni.internal.urls import urlpatterns
        from weni.utils.app_config import update_urlpatterns

        update_urlpatterns(urlpatterns)
