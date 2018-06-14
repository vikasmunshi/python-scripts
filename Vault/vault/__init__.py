#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  vault/__init__.py:
#

from .client_cli import ClientCLI, unlock_device
from .primitives import decrypt, decrypt_and_encrypt, encrypt, merge, split
from .vault import Agent, Vault

__package__ = 'vault'
