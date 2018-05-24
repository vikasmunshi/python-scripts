#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#   crypt/utils.py
#
########################################################################################################################
#    Author: Vikas Munshi <vikas.munshi@gmail.com>
#    Version 0.0.1: 2018.05.24
#
#    source: https://github.com/vikasmunshi/python-scripts/tree/master/src/
#    set-up: bash <(curl -s https://github.com/vikasmunshi/python-scripts/tree/master/src/setup.sh)
#    usage: utils.py uuid filename(s)
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

from re import compile
from uuid import uuid4

re_match_uuid = compile(u'UUID|[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}')


def replace_uuids(string: str) -> (str, list):
    result = re_match_uuid.sub(repl=lambda _: str(uuid4()), string=string)
    return result, re_match_uuid.findall(result)


def change_uuids(*args) -> None:
    for filename in args:
        try:
            with open(filename, 'r') as infile:
                data, new_uuids = replace_uuids(infile.read())
            with open(filename, 'w') as outfile:
                outfile.write(data)
        except Exception as e:
            print(e)
            print('error processing file ' + filename)
        else:
            print('uuids updated in file ' + filename)
            print('\n'.join(new_uuids))


def usage() -> None:
    print('Usage:\n\t' + argv[0] + ' uuid filename(s)')


if __name__ == '__main__':
    from sys import argv

    if len(argv) == 1:
        usage()
    elif argv[1] == 'uuid':
        change_uuids(*argv[2:])
    else:
        usage()
