#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  vault/client_cli.py:
#

from os.path import dirname, join

from .primitives import load_from_file
from .transport import list_files
from .vault import Agent, Vault


class ClientCLI(Agent):
    def __init__(self, agent_id: str, address: str, key_file: str):
        with open(key_file, 'r') as infile:
            pvt_key = infile.read()
        super().__init__(agent_id, address, pvt_key)

    def receive_shares_from_transport(self) -> None:
        for share_file in list_files(self.agent_id + '_secret'):
            share_data = load_from_file(share_file)
            self.load_share_from_transport(share_data)

    def process_requests_from_transport(self) -> None:
        for request_file in list_files(self.agent_id + '_vault'):
            request_data = load_from_file(request_file)
            vault_id = request_data['vault_id']
            vault_pub_key = request_data['vault_pub_key']
            secret_id = request_data['secret_id']
            self.send_share_to_vault(vault_id, vault_pub_key, secret_id)


def unlock_device(device: str, inventory_file: str = '/usr/local/bin/Vault/inventory.json') -> str:
    inventory = load_from_file(inventory_file)
    vault_id = inventory['vault_id']
    vault_key = inventory.get('vault_key')
    if vault_key:
        with open(vault_key, 'r') as infile:
            rsa_key = infile.read()
    else:
        rsa_key = None
    vault = Vault(vault_id=vault_id, custodians=inventory['custodians'], rsa_key=rsa_key)
    secret_id = inventory['disks'][device]
    params = inventory['secrets'][secret_id]
    vault.load_secret(secret_id=secret_id, params=params)
    return vault.open_disk(device=device, passphrase_id=secret_id)
