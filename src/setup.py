#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  setup.py
#
from setuptools import setup

setup(
    name='crypt',
    version='0.0.1',
    author='Vikas Munshi',
    author_email='vikas.munshi@gmail.com',
    url='https://github.com/vikasmunshi/python-scripts/tree/master/src/crypt',
    description='package for persisting secrets securely as shares distributed across custodians',
    packages=['crypt'],
    package_dir={'crypt': 'crypt'},
    package_data={'crypt': 'inventory/*.json'},
    install_requires=['pycryptodome>=3.6.1']
)
