# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['autogoal_telegram']

package_data = \
{'': ['*']}

install_requires = \
['autogoal-contrib==0.8.0',
 'autogoal==1.0.1a1',
 'python-telegram-bot==13',
 'telegram>=0.0.1,<0.0.2']

setup_kwargs = {
    'name': 'autogoal-telegram',
    'version': '0.8.0',
    'description': 'telegram library wrapper for AutoGOAL',
    'long_description': '# AutoGOAL TELEGRAM Algorithm Library',
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
