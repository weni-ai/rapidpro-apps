# RapidPro Apps: Contacts Extension

To work properly, the `contacts_ext` app must be in `$PROJECT_ROOT/apps` directory. Once in it, include on project 
settings:

**settings.py**
```python
from .settings_common import *

# ...
INSTALLED_APPS = INSTALLED_APPS + (
    # ...
    "apps.contacts_ext.apps.ContactsExtConfig",
)
```

This will allow to automatically include the urls in API scope: `temba.api.v2.urls.urlpatterns`.

The final step is apply the migrations:

```shell
$ python manage.py migrate contacts_ext
```
