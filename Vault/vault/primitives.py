#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  vault/primitives.py:
#
from base64 import b64decode, b64encode
from binascii import hexlify, unhexlify
from bisect import bisect_left
from io import BytesIO, TextIOWrapper
from json import load, loads
from operator import itemgetter
from random import SystemRandom
from string import ascii_letters, digits
from typing import Dict, IO, Sequence, Tuple, Union

from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes


def decrypt(msg: str, private_key: Union[str, RSA.RsaKey]) -> str:
    """decrypt (encrypted) msg using private key"""
    rsa_key = private_key if isinstance(private_key, RSA.RsaKey) else RSA.import_key(private_key)
    key_size = rsa_key.size_in_bytes()
    enc_msg = BytesIO(b64decode(msg.encode()))
    enc_encryption_key, nonce, tag, cipher_text = [enc_msg.read(size) for size in (key_size, 16, 16, -1)]
    encryption_key = PKCS1_OAEP.new(rsa_key).decrypt(enc_encryption_key)
    cipher_aes = AES.new(encryption_key, AES.MODE_EAX, nonce)
    return cipher_aes.decrypt_and_verify(cipher_text, tag).decode()


def encrypt(msg: str, public_key: Union[str, RSA.RsaKey]) -> str:
    """encrypt msg using public key"""
    encryption_key = get_random_bytes(32)
    rsa_key = public_key if isinstance(public_key, RSA.RsaKey) else RSA.import_key(public_key)
    enc_encryption_key = PKCS1_OAEP.new(rsa_key).encrypt(encryption_key)
    cipher_aes = AES.new(encryption_key, AES.MODE_EAX)
    cipher_text, tag = cipher_aes.encrypt_and_digest(msg.encode())
    return b64encode(enc_encryption_key + cipher_aes.nonce + tag + cipher_text).decode()


def decrypt_and_encrypt(enc_msg: str, private_key: Union[str, RSA.RsaKey], public_key: Union[str, RSA.RsaKey]) -> str:
    """decrypt (encrypted) msg and (re)encrypt using public key"""
    decryption_private_key = private_key if isinstance(private_key, RSA.RsaKey) else RSA.import_key(private_key)
    encryption_public_key = public_key if isinstance(public_key, RSA.RsaKey) else RSA.import_key(public_key)
    return encrypt(msg=decrypt(msg=enc_msg, private_key=decryption_private_key), public_key=encryption_public_key)


# pre-calculated list of (mersenne) primes 6972593, 13466917, 20996011, 24036583, 25964951, 30402457, 32582657, 37156667
primes = [(2 ** e) - 1 for e in (1279, 2203, 2281, 3217, 4253, 4423, 9689, 9941, 11213, 19937, 21701, 23209, 44497,
                                 86243, 110503, 132049, 216091, 756839, 859433, 1257787, 1398269, 2976221, 3021377)]

# random number generator used to generate randint for use as polynomial coefficients
rand = SystemRandom()


def str_to_int(str_arg: str) -> int:
    """map string to int"""
    return int(hexlify(str_arg.encode('utf-8')), 16)


def int_to_str(int_arg: int) -> str:
    """reverse map int to string"""
    return unhexlify(format(int_arg, 'x')).decode('utf-8')


def egcd(a: int, b: int) -> Tuple[int, int, int]:
    """Euler's extended algorithm for GCD"""
    if a == 0:
        return b, 0, 1
    else:
        g, y, x = egcd(b % a, a)
        return g, x - (b // a) * y, y


def modulo_inverse(x: int, n: int) -> int:
    """multiplicative inverse of x in modulo group n"""
    return (n + egcd(n, abs(x % n))[2]) % n


def polynomial(x: int, coefficients: Sequence[int], n: int) -> int:
    """value at x of polynomial with given coefficients in modulo field n"""
    y = 0
    for i, a in enumerate(coefficients):
        y = (y + (a * (x ** i) % n) % n) % n
    return y


def get_random_str(length: int = 32) -> str:
    """return a random alphanumeric string, default length 32 chars i.e. 256 bits"""
    return ''.join([rand.choice(ascii_letters + digits) for _ in range(length)])


class Share(dict):
    """share is a point on the discreet x,y plane"""

    def __init__(self, x: int, y: int):
        super().__init__(x=x, y=y)


def merge(shares: Sequence[Union[Share, Dict]]) -> str:
    """reconstruct secret from sequence of shares"""
    modulus = primes[bisect_left(primes, max(shares, key=itemgetter('y'))['y'])]
    threshold = len(shares)
    y_intercept = 0
    for i in range(threshold):
        numerator, denominator = 1, 1
        for j in range(threshold):
            if i != j:
                numerator = (numerator * (0 - shares[j]['x'])) % modulus
                denominator = (denominator * (shares[i]['x'] - shares[j]['x'])) % modulus
        lagrange_polynomial = numerator * modulo_inverse(denominator, modulus)
        y_intercept = (modulus + y_intercept + (shares[i]['y'] * lagrange_polynomial)) % modulus
    return int_to_str(y_intercept)


def split(secret: str, threshold: int, num_shares: int) -> Sequence[Share]:
    """split secret into shares such that threshold number or more are required to reconstruct"""
    y_intercept = str_to_int(secret)
    modulus = primes[bisect_left(primes, y_intercept)]  # throws IndexError if secret is too large
    coefficients = (y_intercept,) + tuple(map(lambda _: rand.randint(1, modulus - 1), range(threshold - 1)))
    x_vals = tuple(set([rand.randint(1, 999999) for _ in range(num_shares)]))
    for _ in range(num_shares - len(x_vals)):
        x_vals += (max(x_vals) + 1,)
    return tuple(Share(x, polynomial(x, coefficients, modulus)) for x in x_vals)


def load_from_file(file: Union[str, IO]) -> any:
    """load an object from file on disk or file-like object"""
    if isinstance(file, TextIOWrapper):
        return loads(file.read())
    elif isinstance(file, str):
        with open(file, 'r') as infile:
            return load(infile)
