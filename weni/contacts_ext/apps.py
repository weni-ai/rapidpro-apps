from django.apps import AppConfig


class ContactsExtConfig(AppConfig):
    name = "apps.contacts_ext"

    def ready(self):
        from .urls import urlpatterns
        from ..utils.app_config import update_urlpatterns

        update_urlpatterns(urlpatterns)
