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

import binascii
import collections
import functools
import random
import string
import typing

Share = collections.namedtuple('Share', 'n m x y')
rand = random.SystemRandom()


@functools.lru_cache(maxsize=None)
def mersenne_num(m: int) -> int:
    return (2 ** m) - 1


def get_smallest_prime(x: int) -> int:
    for p in (mersenne_num(m) for m in (1279, 2203, 2281, 3217, 4253, 4423, 9689, 9941, 11213, 19937, 21701, 23209,
                                        44497, 86243, 110503, 132049, 216091, 756839, 859433, 1257787, 1398269, 2976221,
                                        3021377, 6972593, 13466917, 20996011, 24036583, 25964951, 30402457)):
        if p >= x:
            return p
    raise IndexError(x)


def str_to_int(str_arg: str) -> int:
    """map string to int"""
    return int(binascii.hexlify(str_arg.encode('utf-8')), 16)


def int_to_str(int_arg: int) -> str:
    """reverse map int to string"""
    return binascii.unhexlify(format(int_arg, 'x')).decode('utf-8')


def modulo_inverse(x: int, n: int) -> int:
    """multiplicative inverse of x in modulo group n"""

    def egcd(a: int, b: int) -> typing.Tuple[int, int, int]:
        """Euler's extended algorithm for GCD"""
        if a == 0:
            return b, 0, 1
        else:
            g, y, x = egcd(b % a, a)
            return g, x - (b // a) * y, y

    return (n + egcd(n, abs(x % n))[2]) % n


def polynomial(x: int, coefficients: typing.Sequence[int], n: int) -> int:
    """value at x of polynomial with given coefficients in modulo field n"""
    y = 0
    for i, a in enumerate(coefficients):
        y = (y + (a * (x ** i) % n) % n) % n
    return y


def get_random_str(length: int = 32) -> str:
    """return a random alphanumeric string, default length 32 chars i.e. 256 bits"""
    return ''.join([rand.choice(string.ascii_letters + string.digits) for _ in range(length)])


def merge(shares: typing.Sequence[typing.Union[Share, typing.Dict]]) -> typing.Union[str, None]:
    """reconstruct secret from sequence of shares"""
    modulus = get_smallest_prime(max([share.y for share in shares]))
    threshold = shares[0].n
    y_intercept = 0
    try:
        for i in range(threshold):
            numerator, denominator = 1, 1
            for j in range(threshold):
                if i != j:
                    numerator = (numerator * (0 - shares[j].x)) % modulus
                    denominator = (denominator * (shares[i].x - shares[j].x)) % modulus
            lagrange_polynomial = numerator * modulo_inverse(denominator, modulus)
            y_intercept = (modulus + y_intercept + (shares[i].y * lagrange_polynomial)) % modulus
        return int_to_str(y_intercept)
    except (IndexError, UnicodeError):
        return None


def split(secret: str, threshold: int, num_shares: int) -> typing.Sequence[Share]:
    """split secret into shares such that threshold number or more are required to reconstruct"""
    y_intercept = str_to_int(secret)
    modulus = get_smallest_prime(y_intercept)
    coefficients = (y_intercept,) + tuple(map(lambda _: rand.randint(1, modulus - 1), range(threshold - 1)))
    x_vals = tuple(set([rand.randint(1, 999999) for _ in range(num_shares)]))
    for _ in range(num_shares - len(x_vals)):
        x_vals += (max(x_vals) + 1,)
    return tuple(Share(threshold, num_shares, x, polynomial(x, coefficients, modulus)) for x in x_vals)


if __name__ == '__main__':
    secret = get_random_str(length=32)
    shares = split(secret=secret, threshold=3, num_shares=5)
    result = secret == merge(shares=shares[0:3])
    print(result)
    exit(result)
