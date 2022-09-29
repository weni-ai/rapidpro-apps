# RapidPro Apps: Ticketer Queues

To enable this app, add `weni.ticketer_queues` into `INSTALLED_APPS` setting.

Example:
```python
...

INSTALLED_APPS = INSTALLED_APPS + (
    # ...
    "weni.ticketer_queues",
)
```

This will allow to automatically include the urls in API scope: `temba.api.v2.urls.urlpatterns`.
