# RapidPro Apps

To use this apps, clone the repository into `$PROJECT_ROOT/apps` and include on `INSTALLED_APPS` the name that point to
`apps.<app_name>.apps.AppNameConfig`. This will load all necessary URLs and its documentation.

> **Note:** It's possible choose other location. However, application URLs will need to be included in
> `temba.api.v2.urls.urlpatterns` using different methods as well as the API documentation.

A good way to copy to the right path is executing the command bellow:
```shell script
$ git submodule add <remote-address> apps
```

## APPs available

- [Channel Stats](channel_stats/README.md);
- [Contact Extension](contacts_ext/README.md).
