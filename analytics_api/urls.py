from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns

from .views import ContactAnalyticsEndpoint

urlpatterns = [
    url(r"^analytics_api/contacts/$", ContactAnalyticsEndpoint.as_view(),
        name="api.v2.analytics_api.contacts")
]

urlpatterns = format_suffix_patterns(urlpatterns, allowed=["json", "api"])
