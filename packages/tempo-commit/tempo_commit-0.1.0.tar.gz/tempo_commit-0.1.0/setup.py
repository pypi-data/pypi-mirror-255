# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['src', 'src.services']

package_data = \
{'': ['*']}

install_requires = \
['aiofiles>=23.2.1,<24.0.0',
 'asyncclick>=8.1.7.1,<9.0.0.0',
 'gitpython>=3.1.41,<4.0.0',
 'httpx>=0.26.0,<0.27.0',
 'jira[cli]>=3.6.0,<4.0.0',
 'loguru>=0.7.2,<0.8.0',
 'pydantic-settings>=2.1.0,<3.0.0']

entry_points = \
{'console_scripts': ['commit = src.cli:commit', 'init = src.cli:init']}

setup_kwargs = {
    'name': 'tempo-commit',
    'version': '0.1.0',
    'description': 'A cli tool to add a worklog to Tempo on commit',
    'long_description': 'None',
    'author': 'Dinmukhamet Igissinov',
    'author_email': 'igissinov.d@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
