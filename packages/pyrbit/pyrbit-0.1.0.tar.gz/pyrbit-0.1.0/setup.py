# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pyrbit']

package_data = \
{'': ['*']}

install_requires = \
['Sphinx<=7.0',
 'arviz>=0.15.1,<0.16.0',
 'matplotlib>=3.7.1,<4.0.0',
 'numpy>=1.24.2,<2.0.0',
 'pymc>=5.6.0,<6.0.0',
 'scipy>=1.10.1,<2.0.0',
 'seaborn>=0.12.2,<0.13.0',
 'sphinx-rtd-theme>=1.3.0,<2.0.0',
 'statsmodels>=0.14.0,<0.15.0',
 'sympy>=1.12,<2.0',
 'tqdm>=4.65.0,<5.0.0']

setup_kwargs = {
    'name': 'pyrbit',
    'version': '0.1.0',
    'description': 'Utilities for parametric modeling of Recall based interaction techniques',
    'long_description': None,
    'author': 'jgori',
    'author_email': 'juliengori@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.12',
}


setup(**setup_kwargs)
