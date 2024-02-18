# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['autogoal_nltk', 'autogoal_nltk.tests']

package_data = \
{'': ['*']}

install_requires = \
['autogoal-contrib==0.8.1',
 'autogoal==1.0.1a1',
 'gensim==4.1',
 'nltk>=3.8.1,<4.0.0',
 'numpy>=1.21.6,<2.0.0']

setup_kwargs = {
    'name': 'autogoal-nltk',
    'version': '0.8.1',
    'description': 'Scikit-learn algorithm library wrapper for AutoGOAL',
    'long_description': '# AutoGOAL NLTK Algorithm Library',
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
