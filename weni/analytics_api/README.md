# RapidPro Apps: Analytics API

To enable this app, add `weni.analytics_api` to your INSTALLED_APPS setting.

Example:

**settings.py**
```python
...

INSTALLED_APPS = INSTALLED_APPS + (
    ...
    "weni.analytics_api",
)
```

This will allow to automatically include the urls in API scope: `temba.api.v2.urls.urlpatterns`.
