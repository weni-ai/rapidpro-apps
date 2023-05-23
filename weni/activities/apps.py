from django.apps import AppConfig


class ActivitiesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "weni.activities"

    def ready(self) -> None:
        from weni.activities import signals  # noqa: F401
