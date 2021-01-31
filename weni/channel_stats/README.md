# RapidPro Apps: Channel Stats

To enable this app, add `weni.channel_stats` into `INSTALLED_APPS` setting.

Example:
```python
...

INSTALLED_APPS = INSTALLED_APPS + (
    # ...
    "weni.channel_stats",
)
```

This will allow to automatically include the urls in API scope: `temba.api.v2.urls.urlpatterns`.
