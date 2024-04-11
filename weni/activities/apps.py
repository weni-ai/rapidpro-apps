from django.apps import AppConfig
from django.conf import settings


class ActivitiesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "weni.activities"

    def ready(self) -> None:
        if not settings.TESTING:
            from weni.activities import signals  # noqa: F401
