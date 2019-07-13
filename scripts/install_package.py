#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-
from collections import namedtuple
from distutils.version import LooseVersion
from importlib import import_module
from subprocess import PIPE, call
from sys import executable

InstallStatus = namedtuple('InstallStatus', ('status', 'package', 'version'))
InstallStatus.__str__ = lambda self: 'For package {3} installed version {4} is {0}{1}\033[0m'.format(
    '\033[94m' if self.status else '\033[91m', 'ok' if self.status else 'not ok', *self)


def install(package: str, version: str = '') -> InstallStatus:
    required_version = LooseVersion(version or '0')
    installed_version = get_version(package)
    if installed_version is None or installed_version < required_version:
        call([executable, '-m', 'pip', 'install', package, '--upgrade'], stdout=PIPE, stderr=PIPE)
        installed_version = get_version(package)
    return InstallStatus(installed_version >= required_version if installed_version else False,
                         package, str(installed_version))


def get_version(package: str) -> LooseVersion:
    try:
        installed = import_module(package)
    except ImportError:
        pass
    else:
        return LooseVersion(installed.__version__)


if __name__ == '__main__':
    from sys import argv

    for arg in argv[1:]:
        print(install(*arg.split('.', 1)))
