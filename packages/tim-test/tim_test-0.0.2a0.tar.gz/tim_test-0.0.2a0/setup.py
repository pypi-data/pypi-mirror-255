# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['tim_test']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'tim-test',
    'version': '0.0.2a0',
    'description': '',
    'long_description': '# Building tim_test',
    'author': 'Y',
    'author_email': 'None',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
