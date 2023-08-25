from django.urls import re_path
from rest_framework.urlpatterns import format_suffix_patterns

from . import views

urlpatterns = [
    re_path(r"^channel_stats$", views.ChannelStatsEndpoint.as_view(), name="api.v2.channel_stats.channels",),
]

urlpatterns = format_suffix_patterns(urlpatterns, allowed=["json", "api"])
