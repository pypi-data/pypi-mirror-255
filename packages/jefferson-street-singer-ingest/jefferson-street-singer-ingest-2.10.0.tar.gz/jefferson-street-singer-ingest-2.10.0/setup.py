# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['jefferson_street_singer_ingest',
 'jefferson_street_singer_ingest.services',
 'jefferson_street_singer_ingest.services.entry',
 'jefferson_street_singer_ingest.services.state',
 'jefferson_street_singer_ingest.services.stream',
 'jefferson_street_singer_ingest.services.tap',
 'jefferson_street_singer_ingest.services.target']

package_data = \
{'': ['*']}

install_requires = \
['fastavro>=1.6.1,<2.0.0',
 'google-api-python-client>=2.64.0,<3.0.0',
 'google-cloud-storage>=2.5.0,<3.0.0',
 'google>=3.0.0,<4.0.0',
 'mergedeep>=1.3.4,<2.0.0',
 'pandas>=1.4.4,<2.0.0',
 'rec-avro>=0.0.4,<0.0.5',
 'requests>=2.28.1,<3.0.0',
 'singer-sdk==0.1.6']

setup_kwargs = {
    'name': 'jefferson-street-singer-ingest',
    'version': '2.10.0',
    'description': 'Library holding the taps and targets for Jefferson Street Ingestion',
    'long_description': '',
    'author': 'Nikolai McFall',
    'author_email': 'nikolai@jeffersonst.io',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.9',
}


setup(**setup_kwargs)
