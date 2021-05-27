# RapidPro Apps: Template Message

To enable this app, add `weni.template_message` into `INSTALLED_APPS` setting.

Example:
```python
...

INSTALLED_APPS = INSTALLED_APPS + (
    # ...
    "weni.template_message",
)
```

This will allow to automatically include the urls in API scope: `temba.api.v2.urls.urlpatterns`.
