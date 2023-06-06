# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['weni',
 'weni.analytics_api',
 'weni.auth',
 'weni.channel_stats',
 'weni.flows.channel',
 'weni.grpc.billing',
 'weni.grpc.channel',
 'weni.grpc.classifier',
 'weni.grpc.core',
 'weni.grpc.core.management',
 'weni.grpc.core.management.commands',
 'weni.grpc.flow',
 'weni.grpc.org',
 'weni.grpc.statistic',
 'weni.grpc.user',
 'weni.internal',
 'weni.internal.activities',
 'weni.internal.flows',
 'weni.internal.migrations',
 'weni.internal.orgs',
 'weni.internal.tests',
 'weni.internal.tickets',
 'weni.internal.tickets.tests',
 'weni.internal.users',
 'weni.serializers',
 'weni.template_message',
 'weni.templates',
 'weni.ticketer_queues',
 'weni.utils']

package_data = \
{'': ['*']}

install_requires = \
['django-csp>=3.7,<4.0',
 'django-environ>=0.7.0,<0.8.0',
 'django-templates-macros>=0.2,<0.3',
 'djangogrpcframework>=0.2.1,<0.3.0',
 'drf-nested-routers>=0.93.4,<0.94.0',
 'elastic-apm>=6.4.0,<7.0.0',
 'flower>=0.9,<0.10',
 'mozilla-django-oidc>=2.0.0,<3.0.0',
 'pre-commit>=2.20.0,<3.0.0',
 'weni-protobuffers==1.2.18']

setup_kwargs = {
    'name': 'weni-rp-apps',
    'version': '1.0.28',
    'description': 'Weni apps for Rapidpro Platform',
    'long_description': 'None',
    'author': 'jcbalmeida',
    'author_email': 'None',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
