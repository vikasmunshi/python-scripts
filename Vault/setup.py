#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  vault/setup.py:
#
from setuptools import setup

setup(
    name="vault",
    version="0.0.1",
    author="Vikas Munshi",
    author_email="vikas.munshi@gmail.com",
    description="secured secrets",
    packages=['vault', ],
    install_requires=['pycryptodome>=3.6.1', 'inotify>=0.2.9']
)
