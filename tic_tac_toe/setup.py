#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#   tic_tac_toe/setup.py
from setuptools import setup

setup(
    name='tic_tac_toe',
    version='1.0.0',
    author='Vikas Munshi',
    author_email='vikas.munshi@gmail.com',
    url='https://github.com/vikasmunshi/python-scripts/tree/master/tic_tac_toe',
    description='Play Tic Tac Toe Tournament',
    packages=['tic_tac_toe', 'tic_tac_toe.strategies'],
    package_dir={'tic_tac_toe': '.'},
    install_requires=[],
    license='MIT License',
    platforms=['any'],
    long_description=open('README.md').read()
)