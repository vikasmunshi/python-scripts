#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# setup.py
from setuptools import setup

setup(
    name='akira',
        version='1.3.1',
    author='Vikas Munshi',
    author_email='vikas.munshi@gmail.com',
    url='https://github.com/vikasmunshi/python-scripts.git',
    description='Poetry in Python',
    packages=['tic_tac_toe', 'tic_tac_toe.strategies'],
    package_dir={'tic_tac_toe': 'tic_tac_toe'},
        package_data={'tic_tac_toe': 'tic_tac_toe/memory.json'},
    install_requires=[],
    license='MIT License',
    platforms=['any'],
    long_description=open('README.md').read()
)