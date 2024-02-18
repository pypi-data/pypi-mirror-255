# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['jefferson_street_composer',
 'jefferson_street_composer.services',
 'jefferson_street_composer.services.specifications']

package_data = \
{'': ['*']}

install_requires = \
['apache-airflow-providers-cncf-kubernetes>=7.14.0,<8.0.0',
 'apache-airflow==2.7.1']

setup_kwargs = {
    'name': 'jefferson-street-composer',
    'version': '1.3.1',
    'description': 'Library for Jefferson Street Technologies Composer Configuration',
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
