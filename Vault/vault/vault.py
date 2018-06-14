#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  vault/vault.py:
#

from multiprocessing.pool import ThreadPool
from typing import Callable, List, Sequence, Union, TypeVar

from .disks import open_device
from .primitives import RSA, Share, decrypt, decrypt_and_encrypt, encrypt, get_random_str, merge, split, load_from_file
from .transport import send, list_files, receive_files

T = TypeVar('T')


def run_parallel(func: Callable[..., T], func_args_iterable: Sequence[Union[Sequence, any]]) -> List[T]:
    if func_args_iterable:
        def eval_func(func_args: Union[tuple, list, dict]) -> T:
            type_func_args = type(func_args)
            if type_func_args is tuple:
                return func(*func_args)
            elif type_func_args is list:
                return func(*func_args)
            elif type_func_args is dict:
                return func(**func_args)
            else:
                return func(func_args)

        thread_pool = ThreadPool(len(func_args_iterable))
        results = thread_pool.map(eval_func, func_args_iterable)
        thread_pool.close()
        thread_pool.join()
        return results
    return []


class CannotDecryptException(Exception):
    pass


class Agent(dict):
    def __init__(self, agent_id: str, address: str, rsa_key: Union[str, RSA.RsaKey]):
        self.key = rsa_key if isinstance(rsa_key, RSA.RsaKey) else RSA.importKey(rsa_key)
        self.can_decrypt = self.key.has_private()
        self.pub_key = self.key.publickey() if self.can_decrypt else self.key
        self.agent_id = agent_id
        self.address = address
        self.shares = {}
        super().__init__(agent_id=self.agent_id, address=self.address,
                         pub_key=self.pub_key.export_key(format='OpenSSH').decode(), shares=self.shares)

    def encrypt(self, msg: str) -> str:
        return encrypt(msg, self.key.publickey())

    def decrypt(self, enc_msg: str) -> str:
        if self.can_decrypt:
            return decrypt(enc_msg, self.key)
        else:
            raise CannotDecryptException('{} instance does not have private key to decrypt'.format(self.__class__))

    def add_share(self, secret_id: str, x: int, y: int, n: int, m: int) -> None:
        self.shares[secret_id] = {'x': x, 'y': self.encrypt(str(y)), 'n': n, 'm': m}

    def send_share_via_transport(self, secret_id: str) -> None:
        payload = {secret_id: self.shares[secret_id]}
        send(sender=secret_id, receiver=self.agent_id, payload=payload)

    def load_share_from_transport(self, data: dict) -> None:
        for secret_id, share in data.items():
            self.shares[secret_id] = share

    def send_share_to_vault(self, vault_id: str, recipient_key: RSA.RsaKey, secret_id: str) -> None:
        def prepare(secret_id: str) -> dict:
            share = self.shares.get(secret_id)
            if share is not None:
                y_recipient = decrypt_and_encrypt(share['y'], self.key, recipient_key)
                return {k: y_recipient if k == 'y' else v for k, v in share.items()}
            return {}

        share = prepare(secret_id)
        response_id = '{}_{}'.format(secret_id, self.agent_id)
        send(sender=response_id, receiver=vault_id, payload=share)


class Vault(dict):
    def __init__(self, vault_id: str, custodians: dict, rsa_key: Union[str, RSA.RsaKey, None] = None):
        self.vault_id = vault_id
        self.custodians = run_parallel(lambda agent_id, params: Agent(agent_id, params['address'], params['rsa_key']),
                                       list(custodians.items()))
        self.secrets = {}
        self.secret_ids = []
        if rsa_key is None:
            key = RSA.generate(2048)
        else:
            key = rsa_key if isinstance(rsa_key, RSA.RsaKey) else RSA.importKey(rsa_key)
        self.pub_key = key.publickey().export_key(format='OpenSSH').decode()
        self.decrypt = lambda enc_msg: decrypt(enc_msg, key)
        super().__init__(vault_id=self.vault_id, secret_ids=self.secret_ids, custodians=self.custodians)

    def load_secret(self, secret_id: str, params: dict) -> None:
        self.set_secret_from_inventory(secret_id, **params)

    def open_disk(self, device: str, passphrase_id: str) -> str:
        return open_device(device, self.secrets[passphrase_id])

    def set_secret_from_value(self, secret_id: str, value: str) -> None:
        self.secrets[secret_id] = value
        self.secret_ids.append(secret_id)

    def set_secret_from_random(self, secret_id: str, length: int = 32) -> None:
        self.set_secret_from_value(secret_id, get_random_str(length))

    def set_secret_from_shares(self, secret_id: str, shares: Sequence[dict]) -> None:
        shares = [Share(x=share['x'], y=int(self.decrypt(share['y']))) for share in shares]
        self.set_secret_from_value(secret_id, merge(shares))

    def split_to_custodians(self, secret_id: str, n: int, custodians: Sequence[Agent] = ()) -> None:
        custodians = custodians or self.custodians
        value = self.secrets[secret_id]
        m = len(custodians)
        if not (not value or n <= 1 or m < n):
            shares = split(secret=value, threshold=n, num_shares=m)
            run_parallel(lambda c, s: c.add_share(secret_id, s['x'], s['y'], n, m), list(zip(custodians, shares)))

    def set_secret_from_inventory(self, secret_id: str, **kwargs) -> None:
        share_files = [fn for fn in list_files('custodian') if fn.split('_')[1].split('.')[0] == secret_id]
        if len(share_files) < len(self.custodians):
            pass  # To Be Fixed
        if True:
            self.set_secret_from_random(secret_id, kwargs.get('length', 32))
            self.split_to_custodians(secret_id, max(kwargs.get('threshold_shares', 3), 2))
            run_parallel(lambda custodian: custodian.send_share_via_transport(secret_id), self.custodians)
        else:
            payload = {'secret_id': secret_id, 'vault_id': self.vault_id, 'vault_pub_key': self.pub_key}
            threshold = max(kwargs.get('threshold_shares', 3), 2)
            req_id = '{}_{}'.format(self.vault_id, secret_id)
            run_parallel(lambda custodian: send(req_id, custodian.agent_id, payload), self.custodians)
            shares = run_parallel(load_from_file,
                                  receive_files(self.vault_id + '_' + secret_id, expected_files=threshold))
            self.set_secret_from_shares(secret_id, shares)

    def get_apply_func(self, secret_id: str, func: Callable[[str], T]) -> Callable[[], T]:
        return func(self.secrets[secret_id])
