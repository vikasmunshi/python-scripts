#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#   crypt/primitives.py:
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
from datetime import datetime
from json import dump
from os import mkdir
from os.path import abspath, dirname, exists, join
from typing import Sequence


class Transport():
    pass


transport_dir = abspath(join(dirname(__file__), 'cache'))
send_dir = join(transport_dir, 'send')
receive_dir = join(transport_dir, 'receive')

for required_dir in (transport_dir, send_dir, receive_dir):
    if not exists(required_dir):
        mkdir(required_dir)


def send(from_address: str, to_address: str, payload: dict) -> str:
    transport_file = str(datetime.now().timestamp()) + '.json'
    transport_data = {'from_address': from_address, 'to_address': to_address, 'payload': payload}
    with open(transport_file, 'w') as outfile:
        dump(obj=transport_data, fp=outfile)
    return transport_file


def receive(from_address: str, to_address: str) -> Sequence[str]:
    transport_file_pattern = '{}_*.*_{}.json'.format(to_address, from_address)

    return '', ''


if __name__ == '__main__':
    send(from_address='sender1@gmail.com', to_address='vikas.munshi@gmail.com', payload={'msg': 'Hi'})
