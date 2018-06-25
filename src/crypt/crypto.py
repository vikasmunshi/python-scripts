#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#   crypt/crypto.py:
#
########################################################################################################################
#    Author: Vikas Munshi <vikas.munshi@gmail.com>
#    Version 0.0.1: 2018.05.24
#
#    source: https://github.com/vikasmunshi/python-scripts/tree/master/src/
#    set-up: bash <(curl -s https://github.com/vikasmunshi/python-scripts/tree/master/src/setup.sh)
#
########################################################################################################################
#    MIT License
#
#    Copyright (c) 2018 Vikas Munshi
#
#    Permission is hereby granted, free of charge, to any person obtaining a copy
#    of this software and associated documentation files (the "Software"), to deal
#    in the Software without restriction, including without limitation the rights
#    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#    copies of the Software, and to permit persons to whom the Software is
#    furnished to do so, subject to the following conditions:
#
#    The above copyright notice and this permission notice shall be included in all
#    copies or substantial portions of the Software.
#
#    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#    SOFTWARE.
########################################################################################################################

import base64
import io
import typing

from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes

PrivateKey = typing.Union[str, RSA.RsaKey]
PublicKey = typing.Union[str, RSA.RsaKey]


def decrypt(msg: str, private_key: PrivateKey) -> str:
    """decrypt (encrypted) msg using private key"""
    rsa_key = private_key if isinstance(private_key, RSA.RsaKey) else RSA.import_key(private_key)
    key_size = rsa_key.size_in_bytes()
    enc_msg = io.BytesIO(base64.b64decode(msg.encode()))
    enc_encryption_key, nonce, tag, cipher_text = [enc_msg.read(size) for size in (key_size, 16, 16, -1)]
    encryption_key = PKCS1_OAEP.new(rsa_key).decrypt(enc_encryption_key)
    cipher_aes = AES.new(encryption_key, AES.MODE_EAX, nonce)
    return cipher_aes.decrypt_and_verify(cipher_text, tag).decode()


def encrypt(msg: str, public_key: PublicKey) -> str:
    """encrypt msg using public key"""
    encryption_key = get_random_bytes(32)
    rsa_key = public_key if isinstance(public_key, RSA.RsaKey) else RSA.import_key(public_key)
    enc_encryption_key = PKCS1_OAEP.new(rsa_key).encrypt(encryption_key)
    cipher_aes = AES.new(encryption_key, AES.MODE_EAX)
    cipher_text, tag = cipher_aes.encrypt_and_digest(msg.encode())
    return base64.b64encode(enc_encryption_key + cipher_aes.nonce + tag + cipher_text).decode()


def decrypt_and_encrypt(enc_msg: str, private_key: PrivateKey, public_key: PublicKey) -> str:
    """decrypt (encrypted) msg and (re)encrypt using public key"""
    decryption_private_key = private_key if isinstance(private_key, RSA.RsaKey) else RSA.import_key(private_key)
    encryption_public_key = public_key if isinstance(public_key, RSA.RsaKey) else RSA.import_key(public_key)
    return encrypt(msg=decrypt(msg=enc_msg, private_key=decryption_private_key), public_key=encryption_public_key)
