# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['keepass']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.1.7',
 'cryptography>=42.0.1',
 'fastapi>=0.109.0',
 'pykeepass>=4.0.6',
 'uvicorn>=0.27.0']

entry_points = \
{'console_scripts': ['netlink-keepass-fernet-token = '
                     'netlink.keepass.cli:fernet_token_cli',
                     'netlink-keepass-rest-get = '
                     'netlink.keepass.cli:rest_get_cli',
                     'netlink-keepass-rest-reader = '
                     'netlink.keepass.cli:reader_cli',
                     'netlink-keepass-rest-shutdown = '
                     'netlink.keepass.cli:rest_shutdown_cli']}

setup_kwargs = {
    'name': 'netlink-keepass',
    'version': '0.3.1',
    'description': 'Tools to work with (Py)KeePass',
    'long_description': None,
    'author': 'Bernhard Radermacher',
    'author_email': 'bernhard.radermacher@netlink-consulting.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gitlab.com/netlink_python/netlink-keepass.git',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8.1,<3.12',
}


setup(**setup_kwargs)
