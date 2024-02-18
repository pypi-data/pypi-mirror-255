# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['applauncher', 'applauncher.cli', 'applauncher.cli.generate']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=5.4.1,<6.0.0',
 'blinker>=1.4,<2.0',
 'dependency-injector>=4.38.0,<5.0.0',
 'pydantic>=1.7.4,<2.0.0',
 'rich>=9.10.0,<10.0.0',
 'typer>=0.4.0,<0.5.0']

setup_kwargs = {
    'name': 'applauncher',
    'version': '2.3.0',
    'description': 'Python application launcher',
    'long_description': None,
    'author': 'Alvaro Garcia',
    'author_email': 'maxpowel@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
