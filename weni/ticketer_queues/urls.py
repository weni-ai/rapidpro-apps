from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns

from weni.ticketer_queues.views import TicketerQueuesEndpoint

urlpatterns = [
    url(
        r"ticketer_queues$",
        TicketerQueuesEndpoint.as_view(),
        name="api.v2.ticketer_queues",
    )
]

urlpatterns = format_suffix_patterns(urlpatterns, allowed=["json", "api"])
