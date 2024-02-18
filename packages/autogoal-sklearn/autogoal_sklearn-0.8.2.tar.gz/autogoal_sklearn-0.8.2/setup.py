# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['autogoal_sklearn', 'autogoal_sklearn.tests']

package_data = \
{'': ['*']}

install_requires = \
['autogoal-contrib>=0.8.2,<0.9.0',
 'autogoal==1.0.1a1',
 'numpy>=1.21.6,<2.0.0',
 'scikit-learn==1.0',
 'sklearn-crfsuite>=0.3.6,<0.4.0']

setup_kwargs = {
    'name': 'autogoal-sklearn',
    'version': '0.8.2',
    'description': 'scikit-learn algorithm library for AutoGOAL',
    'long_description': '# AutoGOAL Sklearn Algorithm Library',
    'author': 'Suilan Estevez-Velarde',
    'author_email': 'suilanestevez@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://autogoal.github.io',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9.13,<3.10',
}


setup(**setup_kwargs)
