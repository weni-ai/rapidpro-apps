# RapidPro Apps
This package aims to add new apps to Rapidpro without the need to directly change the code, thus avoiding conflicts

# Installing
```sh
$ pip install weni-rp-apps
```


# How to contribute
First, clone this repository
```sh
$ git clone https://github.com/Ilhasoft/rapidpro-apps.git
```

## Setting variables
You need configure the following envireoment variable
- `RAPIDPRO_APPS_PATH` - indicates the path where the repository was cloned
```sh
$ export RAPIDPRO_APPS_PATH="<path>"
```

## Installing the package locally
**OBS**: from now on it is **very important** that it is inside your virtualenv  

After **activating your virtualenv** enter the weni-rp-apps directory
```sh
$ cd $RAPIDPRO_APPS_PATH
```
Run the `install` file
```sh
$ ./install
```

If an error occurs during the installation, the following error will be raised: `There was a problem during the installation`. On the other hand if everything goes well you will receive the following message `Package installed successfully`.  

Done. Now you can go back to rapidpro and help us "Unleash Human Potential"

# Configuring in rapidpro
Add the desired apps to you INSTALLED_APPS setting:

**settings.py**
```python
...

INSTALLED_APPS += ("weni.<app_name>", ...)
```
## APPs available

- [Channel Stats](channel_stats/README.md)
- [Analytics API](analytics_api/README.md)


So that your app can be identify by this script, do you need follow all recomendations of [gRPC Development Patterns](https://github.com/Ilhasoft/rapidpro-apps/wiki/gRPC-Development-Patterns)