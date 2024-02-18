# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cognite',
 'cognite.well_model',
 'cognite.well_model.client',
 'cognite.well_model.client.api',
 'cognite.well_model.client.api.merge_rules',
 'cognite.well_model.client.models',
 'cognite.well_model.client.utils']

package_data = \
{'': ['*']}

install_requires = \
['matplotlib',
 'pandas',
 'pydantic>=1.8,<2.0',
 'requests-oauthlib>=1,<2',
 'requests>=2,<3']

setup_kwargs = {
    'name': 'cognite-wells-sdk',
    'version': '0.18.3',
    'description': '',
    'long_description': 'The well data layer service has been shut down.\nPlease see the [Deprecated and retired features in Cognite Data Fusion (CDF)\n][deprecated].\n\n[deprecated]: https://docs.cognite.com/cdf/deprecated/\n',
    'author': 'Sigurd Holsen',
    'author_email': 'sigurd.holsen@cognite.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8.0,<4.0.0',
}


setup(**setup_kwargs)
