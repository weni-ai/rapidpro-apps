from django.apps import AppConfig


class S3Config(AppConfig):
    name = "weni.s3"

    def ready(self):
        from .urls import urlpatterns
        from ..utils.app_config import update_urlpatterns

        update_urlpatterns(urlpatterns)
