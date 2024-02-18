# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['autogoal_keras']

package_data = \
{'': ['*']}

install_requires = \
['autogoal-contrib==0.8.1',
 'autogoal==1.0.1a1',
 'keras>=2.12.0,<3.0.0',
 'tensorflow>=2.12.0,<3.0.0',
 'tensorflow_addons>=0.22.0,<0.23.0']

setup_kwargs = {
    'name': 'autogoal-keras',
    'version': '0.8.1',
    'description': 'Keras algorithm library wrapper for AutoGOAL',
    'long_description': '# AutoGOAL KERAS Algorithm Library',
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
