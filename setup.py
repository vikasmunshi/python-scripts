#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  setup.py
#
from setuptools import setup

setup(
        name='akira',
        version='0.0.1',
        author='Vikas Munshi',
        author_email='vikas.munshi@gmail.com',
        url='https://github.com/vikasmunshi/python-scripts/tree/master/src/crypt',
        description='package for persisting secrets securely as shares distributed across custodians',
        packages=['crypt'],
        package_dir={'crypt': 'src/crypt'},
        package_data={'crypt': 'inventory/*.json'},
        install_requires=[
                'pycryptodome>=3.6.1',
                'ifaddr>=0.1.4',
                'matplotlib>=3.0.3',
                'numpy>=1.16.3',
                'pandas>=0.24.2',
                'statsmodels>=0.9.0',
                'scipy>=1.3.0',
        ],
        license='MIT License',
        platforms=['any'],
        long_description=open('README.md').read()
)
