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
from io import BytesIO
from json import dumps, load
from os.path import expanduser, join

from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes


def send_share(name: str, address: str, share: dict) -> None:
    # TODO implement Kafka Producer
    share_file = join(expanduser('~/shares_temp/'), '{}.{}.json'.format(address, share['uuid']))
    out = dumps({'name': name, 'address': address, 'share': share}, indent=4)
    with open(share_file, 'w') as outfile:
        outfile.write(out)
    print(out)


def request_share(name: str, address: str, agent: dict, uuid: str) -> None:
    # TODO implement Kafka Producer
    out = dumps({'name': name, 'agent': agent, 'address': address, 'uuid': uuid}, indent=4)
    print(out)


def receive_share(address: str, agent: dict, uuid: str) -> dict:
    # TODO implement Kafka  Consumer

    share_file = join(expanduser('~/shares_temp/'), '{}.{}.json'.format(address, uuid))

    with open(share_file, 'r') as infile:
        share_raw = load(infile)['share']

    private_key_file = join(expanduser('~/shares_temp/'), address.split('@')[0])
    with open(private_key_file, 'r') as infile:
        private_key = RSA.importKey(infile.read())

    cipher_rsa = PKCS1_OAEP.new(private_key)
    key_size = private_key.size_in_bytes()

    # decrypt_share
    enc_y = BytesIO(b64decode(share_raw['y'].encode()))
    enc_encryption_key, nonce, tag, cipher_text = [enc_y.read(size) for size in (key_size, 16, 16, -1)]
    encryption_key = cipher_rsa.decrypt(enc_encryption_key)
    cipher_aes = AES.new(encryption_key, AES.MODE_EAX, nonce)
    share_raw['y'] = int(cipher_aes.decrypt_and_verify(cipher_text, tag).decode())

    # encrypt_share
    encryption_key = get_random_bytes(32)
    enc_encryption_key = PKCS1_OAEP.new(RSA.importKey(agent['public_key'])).encrypt(encryption_key)
    cipher_aes = AES.new(encryption_key, AES.MODE_EAX)
    cipher_text, tag = cipher_aes.encrypt_and_digest(str(share_raw['y']).encode())
    share_raw['y'] = b64encode(enc_encryption_key + cipher_aes.nonce + tag + cipher_text).decode()
    share_raw['agent'] = agent

    return share_raw
