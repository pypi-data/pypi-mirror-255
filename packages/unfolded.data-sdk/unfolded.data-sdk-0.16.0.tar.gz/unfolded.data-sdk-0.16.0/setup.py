# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['data_sdk']

package_data = \
{'': ['*']}

install_requires = \
['PyJWT>=2.0.0,<3.0.0',
 'click>=7.0,<9.0',
 'pydantic>=1.7.0,<2.0.0',
 'requests>=2.31.0,<3.0.0']

extras_require = \
{':python_version < "3.8"': ['typing-extensions>=3.7.4,<4.0.0'],
 'dataframe': ['pandas>=1.0,<2.0'],
 'dataframe:python_version >= "3.8"': ['geopandas>=0.13.2'],
 'query': ['pandas>=1.0,<2.0', 'pyarrow>=6.0.0,<7.0.0'],
 'test': ['pandas>=1.0,<2.0', 'pyarrow>=6.0.0,<7.0.0'],
 'test:python_version >= "3.8"': ['geopandas>=0.13.2']}

entry_points = \
{'console_scripts': ['uf-data-sdk = unfolded.data_sdk.cli:main']}

setup_kwargs = {
    'name': 'unfolded.data-sdk',
    'version': '0.16.0',
    'description': "Module for working with Foursquare Studio's Data SDK",
    'long_description': "# `unfolded.data-sdk`\n\nPython package for interfacing with [Unfolded](https://unfolded.ai)'s Data SDK.\n\nFor more documentation, refer to the [documentation website](https://location.foursquare.com/developer/docs/studio-data-sdk-overview).\n",
    'author': 'Kyle Barron',
    'author_email': 'kbarron@foursquare.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7.1,<4.0.0',
}


setup(**setup_kwargs)
