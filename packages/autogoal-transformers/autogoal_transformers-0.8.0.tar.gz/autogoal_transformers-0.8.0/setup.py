# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['autogoal_transformers']

package_data = \
{'': ['*']}

install_requires = \
['autogoal-contrib==0.8.0',
 'autogoal==1.0.1a1',
 'datasets>=2.14.6,<3.0.0',
 'evaluate>=0.4.1,<0.5.0',
 'torch>=2.0.0,<3.0.0',
 'transformers>=4.27.3,<5.0.0']

setup_kwargs = {
    'name': 'autogoal-transformers',
    'version': '0.8.0',
    'description': 'transformers algorithm library wrapper for AutoGOAL',
    'long_description': '# AutoGOAL TRANSFORMERS Algorithm Library',
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
