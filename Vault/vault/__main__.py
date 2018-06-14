#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  vault/__main__.py:
#

from os.path import basename, dirname, join, splitext
from sys import argv

from .client_cli import ClientCLI
from .primitives import load_from_file
from .transport import set_local_cache_dir
from .vault import Vault

if __name__ == '__main__':
    if len(argv) > 1:
        if argv[1] == 'client':
            custodian_key_file = argv[2]
            local_dir = join(dirname(dirname(custodian_key_file)), 'cache')
            set_local_cache_dir(local_dir)
            custodian_id, _ = splitext(basename(custodian_key_file))
            custodian_address = custodian_id
            client_cli = ClientCLI(custodian_id, custodian_address, custodian_key_file)
            client_cli.receive_shares_from_transport()
            client_cli.process_requests_from_transport()
        elif argv[1] == 'test':
            inventory_file = '/usr/local/bin/Vault/inventory.json'
            inventory = load_from_file(inventory_file)
            vault_id = inventory['vault_id']
            vault_key = inventory.get('vault_key')
            if vault_key:
                with open(vault_key, 'r') as infile:
                    rsa_key = infile.read()
            else:
                rsa_key = None
            vault = Vault(vault_id=vault_id, custodians=inventory['custodians'], rsa_key=rsa_key)
            secret_id = 'secret:2ac01012-b4e2-4d93-a8b4-e3f9e587ba99'
            params = inventory['secrets'][secret_id]
            vault.load_secret(secret_id=secret_id, params=params)
            print(vault.secrets)
    else:
        print('{} package'.format(__package__))
