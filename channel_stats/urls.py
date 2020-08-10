from django.conf.urls import url

from . import views

urlpatterns = [
    url(r"^channel_stats/channels(?P<format>\.(json|api))?$", views.ChannelStatsEndpoint.as_view(),
        name="api.v2.channel_stats.channels"),
    url(r"^channel_stats/active_contacts(?P<format>\.(json|api))?$", views.ActiveContactsEndpoint.as_view(),
        name="api.v2.channel_stats.contacts"),
]
