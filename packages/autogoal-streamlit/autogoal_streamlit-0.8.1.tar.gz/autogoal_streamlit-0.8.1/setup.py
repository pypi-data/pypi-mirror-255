# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['autogoal_streamlit']

package_data = \
{'': ['*']}

install_requires = \
['autogoal-contrib==0.8.1',
 'autogoal==1.0.1a1',
 'nx-altair>=0.1.6,<0.2.0',
 'streamlit>=1.20.0,<2.0.0']

setup_kwargs = {
    'name': 'autogoal-streamlit',
    'version': '0.8.1',
    'description': 'streamlit library wrapper for AutoGOAL',
    'long_description': '# AutoGOAL STREAMLIT Algorithm Library',
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
