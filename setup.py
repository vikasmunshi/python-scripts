#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# setup.py
from setuptools import setup

setup(
    name='akira',
    version='1.0.1',
    author='Vikas Munshi',
    author_email='vikas.munshi@gmail.com',
    url='https://github.com/vikasmunshi/python-scripts.git',
    description='Poetry in Python',
    packages=['tic_tac_toe', 'tic_tac_toe.strategies'],
    package_dir={'tic_tac_toe': 'tic_tac_toe'},
    package_data={},
    install_requires=[],
    # install_requires=['pycryptodome>=3.6.1', 'ifaddr>=0.1.4', 'inotify>=0.2.9'],
    license='MIT License',
    platforms=['any'],
    long_description=open('README.md').read()
)
