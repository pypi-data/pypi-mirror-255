# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['experiments',
 'vgd_counterfactuals',
 'vgd_counterfactuals.examples',
 'vgd_counterfactuals.experiments',
 'vgd_counterfactuals.generate']

package_data = \
{'': ['*'],
 'experiments': ['results/*'],
 'vgd_counterfactuals': ['templates/*'],
 'vgd_counterfactuals.experiments': ['results/*']}

install_requires = \
['click>=7.1.2',
 'dimorphite-dl>=1.3.2',
 'jinja2>=3.0.3',
 'matplotlib>=3.5.3',
 'numpy>=1.23.2',
 'poetry-bumpversion>=0.3.0',
 'pycomex>=0.9.2',
 'python-decouple>=3.6',
 'rdkit>=2022.9.5',
 'visual_graph_datasets>=0.13.4']

entry_points = \
{'console_scripts': ['vgd_counterfactuals = vgd_counterfactuals.cli:cli']}

setup_kwargs = {
    'name': 'vgd-counterfactuals',
    'version': '0.3.6',
    'description': 'Counterfactual explanations for GNNs based on the visual graph dataset format',
    'long_description': 'None',
    'author': 'Jonas Teufel',
    'author_email': 'jonseb1998@gmail.com',
    'maintainer': 'Jonas Teufel',
    'maintainer_email': 'jonseb1998@gmail.com',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<=3.12',
}


setup(**setup_kwargs)
