# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['codefly']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=6.0.1,<7.0.0', 'pydantic>=2.5.3,<3.0.0']

setup_kwargs = {
    'name': 'codefly-sdk',
    'version': '0.0.3',
    'description': '',
    'long_description': None,
    'author': 'Antoine Toussaint',
    'author_email': 'antoine.toussaint@codefly.ai',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
