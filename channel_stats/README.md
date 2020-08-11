# RapidPro Apps: Channel Stats

To work properly, the `channel_stats` app must be in `$PROJECT_ROOT/apps` directory. Once in it, include on project 
settings:

**settings.py**
```python
from .settings_common import *

# ...
INSTALLED_APPS = INSTALLED_APPS + (
    # ...
    "apps.channel_stats.apps.ChannelStatsConfig",
)
```

This will allow to automatically include the urls in API scope: `temba.api.v2.urls.urlpatterns`.
