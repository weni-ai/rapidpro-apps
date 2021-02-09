from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns

from .views import ContactAnalyticsEndpoint, FlowRunAnalyticsEndpoint

urlpatterns = [
    url(r"^analytics/contacts/$", ContactAnalyticsEndpoint.as_view(), name="api.v2.analytics.contacts",),
    url(r"^analytics/flow-runs/$", FlowRunAnalyticsEndpoint.as_view(), name="api.v2.analytics.flow_runs",),
]

urlpatterns = format_suffix_patterns(urlpatterns, allowed=["json", "api"])
