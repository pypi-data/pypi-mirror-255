# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dj_temporal']

package_data = \
{'': ['*']}

install_requires = \
['temporalio>=1.5.0,<2.0.0']

setup_kwargs = {
    'name': 'dj-temporal',
    'version': '0.1.0',
    'description': '',
    'long_description': '',
    'author': 'Igor Polynets',
    'author_email': 'polinom100@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.11,<4.0',
}


setup(**setup_kwargs)
