# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['csgen']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'csgen',
    'version': '0.1.0',
    'description': 'Framework for writing generated C# code',
    'long_description': '# csgen\n\n<!-- start badges -->\n\n[pypi]: https://pypi.org/project/csgen/\n\n[![Build](https://github.com/ionite34/csgen/actions/workflows/build.yml/badge.svg)](https://github.com/ionite34/csgen/actions/workflows/build.yml)\n\n[![PyPI](https://img.shields.io/pypi/v/csgen)][pypi]\n[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/csgen)][pypi]\n\n<!-- end badges -->\n\n> Framework for writing generated C# code\n',
    'author': 'ionite34',
    'author_email': 'dev@ionite.io',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.10,<3.13',
}


setup(**setup_kwargs)
