# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dh_facebook_client']

package_data = \
{'': ['*']}

install_requires = \
['backoff>=1.11.1,<2.0.0', 'requests>=2.26.0,<3.0.0']

setup_kwargs = {
    'name': 'dh-facebook-client',
    'version': '0.2.8',
    'description': 'Simple client for interacting with the Facebook Graph API',
    'long_description': '# dh-facebook-client\n',
    'author': 'pchisholm',
    'author_email': 'chisholm.p@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
