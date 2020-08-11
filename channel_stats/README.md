# RapidPro Apps

To work properly, the `channel_stats` app must be in `PROJECT_ROOT/apps` directory. Once in it, include on project 
settings:

Settings:
```python
from .settings_common import *

# ...
INSTALLED_APPS = INSTALLED_APPS + (
    # ...
    "apps.channel_stats.apps.ChannelStatsConfig",
)
```

This will allow to automatically include the urls in API scope: `temba.api.v2.urls.urlpatterns`.

The final step is migrate

```shell
$ python manage.py migrate channel_stats
```

> **Note:** It's possible to add this app as a sub module using the git.
> `$ git submodule add <remote-address> apps`
---

