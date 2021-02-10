# RapidPro Channel Stats

### Add `temba/urls.py`

`from temba.channel_stats.views import ChannelStatsEndpoint  # noqa`

`urlpatterns += [
    url(r"^api/v2/channel_stats\.(?P<format>(json|api))/?$", ChannelStatsEndpoint.as_view(), name="api.v2.channel_stats"),
]`

### Add `temba/settings.prod.py`

`INSTALLED_APPS = (*INSTALLED_APPS, "temba.channel_stats",)`

