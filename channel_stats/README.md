# RapidPro Apps

To work properly, the `channel_stats` app must be in `PROJECT_ROOT/apps` directory. Once in it, include on project 
settings and, optionally, add the middleware to registry the URLs on API explorer:

Settings:
```python
from .settings_common import *

# ...
INSTALLED_APPS = INSTALLED_APPS + (
    # ...
    "apps.channel_stats.apps.ChannelStatsConfig",
)

MIDDLEWARE = MIDDLEWARE + (
    # ...
    "apps.channel_stats.middleware.APIExplorerV2",
)
```

It's possible to add this app as a sub module using the git.

Example:
```shell script
$ git submodule add <remote-address> apps
```

After that, the urls will automatically be included in `temba.api.v2.urls.urlpatterns`.
