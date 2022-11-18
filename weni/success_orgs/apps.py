from django.apps import AppConfig


class SucessOrgsConfig(AppConfig):
    name = "weni.success_orgs"

    def ready(self):
        from weni.success_orgs.urls import urlpatterns
        from weni.utils.app_config import update_urlpatterns

        update_urlpatterns(urlpatterns)
