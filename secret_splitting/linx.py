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

from binascii import hexlify, unhexlify
from bisect import bisect_left
from random import SystemRandom
from typing import Callable, Iterable, Tuple

PRIMES = [(2 ** e) - 1 for e in (1279, 2203, 2281, 3217, 4253, 4423, 9689, 9941, 11213, 19937, 21701, 23209, 44497,
                                 86243, 110503, 132049, 216091, 756839, 859433, 1257787, 1398269, 2976221, 3021377)]
RAND = SystemRandom()


def str_to_int(s: str) -> int:
    return int(hexlify(s.encode('utf-8')), 16)


def int_to_str(i: int) -> str:
    return unhexlify(format(i, 'x')).decode('utf-8')


def modulo_inverse(number: int, modulus: int) -> int:
    def egcd(a: int, b: int) -> (int, int, int):
        if a == 0:
            return b, 0, 1
        else:
            g, y, x = egcd(b % a, a)
            return g, x - (b // a) * y, y

    return (modulus + egcd(modulus, abs(number % modulus))[2]) % modulus


def polynomial(coefficients: Tuple[int], x: int, modulus: int) -> int:
    result = 0
    for i in range(0, len(coefficients) - 1):
        result = (result + (coefficients[i] * (x ** i) % modulus) % modulus) % modulus
    return result


class Share(object):
    def __init__(self, n: int, m: int, x: int, y: int = None, polynomial: Callable[[int], int] = None):
        self.n = n
        self.m = m
        self.x = x
        self.y = y or polynomial(x)

    def __eq__(self, other):
        return self.n == other.n and self.m == other.m and self.x == other.x and self.y == other.y

    def __ne__(self, other):
        return not self == other

    def __lt__(self, other):
        return self.y < other.y

    def __gt__(self, other):
        return self.y > other.y

    def __le__(self, other):
        return self.y <= other.y

    def __ge__(self, other):
        return self.y >= other.y

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return 'Share(n={}, m={}, x={}, y={})'.format(self.n, self.m, self.x, self.y)


class Shares(list):
    def __init__(self, shares: Iterable[Share]):
        n = set([s.n for s in shares])
        assert len(n) == 1
        self.n = tuple(n)[0]
        m = set([s.m for s in shares])
        assert len(m) == 1
        x = set([s.x for s in shares])
        assert len(x) >= self.n
        super().__init__(shares)

    def __str__(self):
        return '\n'.join([repr(s) for s in self])

    def __repr__(self):
        return 'Shares([{}])'.format(', '.join([repr(s) for s in self]))


class Secret(object):
    def __init__(self, secret: str = None, shares: Tuple[Share] = (), n: int = 3, m: int = 5):
        if isinstance(secret, str):
            self.secret = secret
            y_intercept = str_to_int(self.secret)
            modulus = PRIMES[bisect_left(PRIMES, y_intercept)]
            coefficients = (y_intercept,) + tuple(map(lambda _: RAND.randint(1, modulus - 1), range(n)))
            x_vals = tuple(set([RAND.randint(1, 999999) for _ in range(m)]))
            for _ in range(m - len(x_vals)): x_vals += (max(x_vals) + 1,)
            self.shares = Shares([Share(n=n, m=m, x=x, y=polynomial(coefficients, x, modulus)) for x in x_vals])

        elif isinstance(shares, Iterable) and all([isinstance(s, Share) for s in shares]):
            self.shares = Shares(shares)
            modulus = PRIMES[bisect_left(PRIMES, max(self.shares).y)]
            y_intercept = 0
            for i in range(self.shares.n):
                numerator, denominator = 1, 1
                for j in range(self.shares.n):
                    if i != j:
                        numerator = (numerator * (0 - self.shares[j].x)) % modulus
                        denominator = (denominator * (self.shares[i].x - self.shares[j].x)) % modulus
                lagrange_polynomial = numerator * modulo_inverse(denominator, modulus)
                y_intercept = (modulus + y_intercept + (self.shares[i].y * lagrange_polynomial)) % modulus
            self.secret = int_to_str(y_intercept)

        else:
            raise ValueError('either secret or shares (tuple of share) must be provided')

    def __repr__(self):
        return 'Secret({!r})'.format(self.shares)

    def __str__(self):
        return repr(self)


if __name__ == '__main__':
    s = Secret('gwbyrix fjhsauegf gfugr')

    print(s.shares)
    print(Secret(shares=tuple(s.shares)))
