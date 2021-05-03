# RapidPro Apps

## Installing
```shell script
$ pip install -e git+git://github.com/Ilhasoft/rapidpro-apps.git
```

Add the desired apps to you INSTALLED_APPS setting:

**settings.py**
```python
...

INSTALLED_APPS += ("weni.<app_name>", ...)
```
## APPs available

- [Channel Stats](channel_stats/README.md)
- [Analytics API](analytics_api/README.md)

## Use `get_protobuffers.sh`

You need configure the following envireoment variables
- `WENI_PROTO_PATH`
- `RAPIDPRO_APPS_PATH`

```sh
export WENI_PROTO_PATH="<path>"
export RAPIDPRO_APPS_PATH="<path>"
```

After this configurations run the `get_protobuffers.sh`
**OBS**: You need are in directory `RAPIDPRO_APPS_PATH`
```
./get_protobuffers.sh
```

So that your app can be identify by this script, do you need follow all recomendations of [gRPC Development Patterns](https://github.com/Ilhasoft/rapidpro-apps/wiki/gRPC-Development-Patterns)