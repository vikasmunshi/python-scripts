#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

"""

########################################################################################################################
#    MIT License                                                                                                       #
#                                                                                                                      #
#    Copyright (c) 2018 Vikas Munshi <vikas.munshi@gmail.com>                                                          #
#                                                                                                                      #
#    Permission is hereby granted, free of charge, to any person obtaining a copy                                      #
#    of this software and associated documentation files (the "Software"), to deal                                     #
#    in the Software without restriction, including without limitation the rights                                      #
#    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell                                         #
#    copies of the Software, and to permit persons to whom the Software is                                             #
#    furnished to do so, subject to the following conditions:                                                          #
#                                                                                                                      #
#    The above copyright notice and this permission notice shall be included in all                                    #
#    copies or substantial portions of the Software.                                                                   #
#                                                                                                                      #
#    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR                                        #
#    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,                                          #
#    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE                                       #
#    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER                                            #
#    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,                                     #
#    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE                                     #
#    SOFTWARE.                                                                                                         #
########################################################################################################################
from base64 import b64decode, b64encode
from binascii import hexlify, unhexlify
from bisect import bisect_left
from io import BytesIO, TextIOWrapper
from os.path import isfile
from random import SystemRandom
from typing import Callable, IO, Sequence, Union
from uuid import uuid4

from Crypto.Cipher import AES, PKCS1_OAEP  # need pycryptodome, run: sudo -H pip3 install pycryptodome
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes

from .collections import Custodian, Custodians, Share, Shares, run_parallel

rand = SystemRandom()
primes = [(2 ** e) - 1 for e in (1279, 2203, 2281, 3217, 4253, 4423, 9689, 9941, 11213, 19937, 21701, 23209, 44497,
                                 86243, 110503, 132049, 216091, 756839, 859433, 1257787, 1398269, 2976221, 3021377)]


def str_to_int(str_arg: str) -> int:
    return int(hexlify(str_arg.encode('utf-8')), 16)


def int_to_str(int_arg: int) -> str:
    return unhexlify(format(int_arg, 'x')).decode('utf-8')


def modulo_inverse(number: int, modulus: int) -> int:
    def egcd(a: int, b: int) -> (int, int, int):
        if a == 0:
            return b, 0, 1
        else:
            g, y, x = egcd(b % a, a)
            return g, x - (b // a) * y, y

    return (modulus + egcd(modulus, abs(number % modulus))[2]) % modulus


class Agent(object):
    def __init__(self, name: str, private_key: Union[str, IO, None] = None, uuid: str = None):
        self.name = name
        if isinstance(private_key, str) and isfile(private_key):
            with open(private_key, 'r') as infile:
                private_key = RSA.importKey(infile.read())
        elif isinstance(private_key, TextIOWrapper):
            private_key = RSA.importKey(private_key.read())
        elif private_key is None:
            private_key = RSA.generate(2048)
        else:
            raise ValueError('private key must be a filename or file object or None')
        self.public_key = private_key.publickey().export_key(format='OpenSSH').decode()
        self.cipher_rsa = PKCS1_OAEP.new(private_key)
        self.key_size = private_key.size_in_bytes()
        self.uuid = uuid or str(uuid4())

    def decrypt_share(self, share: Share) -> Share:
        enc_y = BytesIO(b64decode(share.y.encode()))
        enc_encryption_key, nonce, tag, cipher_text = [enc_y.read(size) for size in (self.key_size, 16, 16, -1)]
        encryption_key = self.cipher_rsa.decrypt(enc_encryption_key)
        cipher_aes = AES.new(encryption_key, AES.MODE_EAX, nonce)
        share['y'] = int(cipher_aes.decrypt_and_verify(cipher_text, tag).decode())
        return share

    @staticmethod
    def encrypt_share(share: Share, custodian: Custodian) -> Share:
        encryption_key = get_random_bytes(32)
        enc_encryption_key = PKCS1_OAEP.new(RSA.importKey(custodian.pubkey)).encrypt(encryption_key)
        cipher_aes = AES.new(encryption_key, AES.MODE_EAX)
        cipher_text, tag = cipher_aes.encrypt_and_digest(str(share.y).encode())
        share['y'] = b64encode(enc_encryption_key + cipher_aes.nonce + tag + cipher_text).decode()
        return share

    def __repr__(self):
        return repr({'name': self.name, 'uuid': self.uuid, 'public_key': self.public_key})

    def __str__(self):
        return repr(self)


class Secret(object):
    def __init__(self, agent: Agent,
                 secret: Union[Callable[[], str], str] = None, uuid: str = None,
                 n: int = 3, custodians: Custodians = (),
                 shares: Shares = ()):
        if (isinstance(secret, str) or callable(secret)) and isinstance(custodians, Custodians):
            m = len(custodians)
            n = min(n, m)
            secret = secret if isinstance(secret, str) else secret()
            uuid = uuid or str(uuid4())
            shares = self.secret_to_shares(agent=eval(repr(agent)), secret=secret, uuid=uuid, n=n, m=m)
            custodians.assign_shares(shares=shares, transform=lambda s, c: agent.encrypt_share(s, c))
        elif isinstance(shares, Shares):
            shares = Shares(run_parallel(agent.decrypt_share, shares))
            secret = self.shares_to_secret(shares=shares)
        else:
            raise ValueError('either (secret and custodians) or (shares) must be provided')

        self.apply = lambda func: func(secret)
        self.apply.__annotations__['func'] = Callable
        self.apply.__annotations__['return'] = any

    @staticmethod
    def secret_to_shares(agent: dict, secret: str, uuid: str, n: int, m: int) -> Shares:
        y_intercept = str_to_int(secret)
        modulus = primes[bisect_left(primes, y_intercept)]
        coefficients = (y_intercept,) + tuple(map(lambda _: rand.randint(1, modulus - 1), range(n)))

        def polynomial(x: int) -> Share:
            y = 0
            for i in range(0, len(coefficients) - 1):
                y = (y + (coefficients[i] * (x ** i) % modulus) % modulus) % modulus
            return Share(agent=agent, uuid=uuid, num_required=n, num_generated=m, x=x, y=y)

        x_vals = tuple(set([rand.randint(1, 999999) for _ in range(m)]))
        for _ in range(m - len(x_vals)):
            x_vals += (max(x_vals) + 1,)

        return Shares([polynomial(x) for x in x_vals])

    @staticmethod
    def shares_to_secret(shares: Sequence[Share]) -> str:
        modulus = primes[bisect_left(primes, max(shares, key=lambda share: share['y'])['y'])]
        y_intercept = 0
        n = shares[0]['num_required']
        for i in range(n):
            numerator, denominator = 1, 1
            for j in range(n):
                if i != j:
                    numerator = (numerator * (0 - shares[j]['x'])) % modulus
                    denominator = (denominator * (shares[i]['x'] - shares[j]['x'])) % modulus
            lagrange_polynomial = numerator * modulo_inverse(denominator, modulus)
            y_intercept = (modulus + y_intercept + (shares[i]['y'] * lagrange_polynomial)) % modulus
        return int_to_str(y_intercept)
