from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns

from . import views

urlpatterns = [
    url(r"^contacts_ext/active$", views.ActiveContactsEndpoint.as_view(),
        name="api.v2.contacts_ext.active"),
]

urlpatterns = format_suffix_patterns(urlpatterns, allowed=["json", "api"])
