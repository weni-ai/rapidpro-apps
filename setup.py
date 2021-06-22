from setuptools import setup

setup(name="rapidpro-apps", install_requires=[
    "mozilla-django-oidc@git+https://github.com/mozilla/mozilla-django-oidc.git@master",
    "djangogrpcframework",
    "grpcio",
    "grpcio-tools",
    ])
