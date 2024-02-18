# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['pdots']
setup_kwargs = {
    'name': 'pdots',
    'version': '0.2.0',
    'description': 'Progress dots',
    'long_description': 'A simple, infinite progress indicator, as in: there is progress going on (and not: how far along are we)\n',
    'author': 'L3viathan',
    'author_email': 'git@l3vi.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'py_modules': modules,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
