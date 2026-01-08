# RapidPro Apps
This package aims to add new apps to Rapidpro without the need to directly change the code, thus avoiding conflicts

## How to contribute
First, clone this repository
```sh
$ git clone https://github.com/Ilhasoft/rapidpro-apps.git
```
Install dependencies and enter virtualenv
```sh
$ poetry install
$ poetry shell
```
Sync pre-commits to your environment
```sh
$ pre-commit install
```

<br>

## Running (important)
This repository is **not a standalone Django project** (there is no `manage.py` here). It provides Django apps meant to be installed into a **RapidPro** instance (or another Django project).

To test it running, you should run **RapidPro's** `manage.py` after installing this package into the same virtualenv.

<br>

## Install using pip
<details>
<summary>Click to expand</summary><br>

```sh
$ pip install weni-rp-apps
```

</details>

## Local Installation

<details>
<summary>Click to expand</summary><br>

You need configure the following envireoment variable `Necessary for some installations methods`
- `RAPIDPRO_APPS_PATH` - indicates the path where the repository was cloned
```sh
$ export RAPIDPRO_APPS_PATH="<path>"
```
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

</details>
  
## Local Installation - Manual
<details>
<summary>Click to expand</summary><br>
  
```sh
poetry build
```

```sh
cd dist/
tar -xvf weni-rp-apps-1.0.13.tar.gz # Look at specific version
```

```sh
cd weni-rp-apps-1.0.13/ # Look at specific version
python setup.py develop
```
</details>
  
<br>

## Setting variables
Add the desired apps to you INSTALLED_APPS setting:

**settings.py**
```python
...

INSTALLED_APPS += ("weni.<app_name>", ...)
```


Done. Now you can go back to rapidpro and help us "Unleash Human Potential"

## APPs available

- [Channel Stats](channel_stats/README.md)
- [Analytics API](analytics_api/README.md)


So that your app can be identify by this script, do you need follow all recomendations of [gRPC Development Patterns](https://github.com/Ilhasoft/rapidpro-apps/wiki/gRPC-Development-Patterns)
