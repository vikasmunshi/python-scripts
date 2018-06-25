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
from json import dumps, load
from multiprocessing.pool import ThreadPool
from os.path import isfile
from typing import Callable, IO, List, Sequence, Tuple, TypeVar, Union

from .transport import receive_share, request_share, send_share

T = TypeVar('T')


def run_parallel(func: Callable[..., T], func_args_iterable: Sequence[Union[Sequence, any]]) -> List[T]:
    if func_args_iterable:
        thread_pool = ThreadPool(len(func_args_iterable))
        results = thread_pool.map(lambda f_args: func(*f_args) if isinstance(f_args, (tuple, list)) else func(f_args),
                                  func_args_iterable)
        thread_pool.close()
        thread_pool.join()
        return results
    return []


def run_serial(func: Callable[..., T], func_args_iterable: Sequence[Union[Sequence, any]]) -> List[T]:
    results = []
    for f_args in func_args_iterable:
        results.append(func(*f_args) if isinstance(f_args, (tuple, list)) else func(f_args))
    return results


class AttributeDict(dict):
    redacted = ()
    items_for_checking_equality = ()

    @staticmethod
    def redacted_func(x):
        return True

    def __getattr__(self, item):
        return self[item]

    def __repr__(self):
        return repr({k: v for k, v in self.items() if not (k in self.redacted and self.redacted_func(k))})

    def __str__(self):
        return repr(self)

    def __eq__(self, other):
        return not any([self[x] != other[x] for x in self.items_for_checking_equality])

    def __ne__(self, other):
        return any([self[x] != other[x] for x in self.items_for_checking_equality])


class HomogeneousMinTwoTuple(tuple):
    def __new__(cls, sequence: Sequence[T]) -> Tuple[T]:
        assert len(sequence) > 1, 'Require minimum two objects!'
        t = type(sequence[0])
        assert not any([not type(item) is t for item in sequence[1:]]), 'Require all objects to be of same type!'
        return tuple.__new__(cls, sequence)


class Share(AttributeDict):
    def __init__(self, agent: dict, uuid: str, num_required: int, num_generated: int, x: int, y: Union[int, str]):
        super().__init__(agent=agent, uuid=uuid, num_required=num_required, num_generated=num_generated, x=x, y=y)

    redacted = ('y',)
    items_for_checking_equality = ('uuid', 'num_required', 'num_generated')

    @staticmethod
    def redacted_func(x):
        return isinstance(x, int)


class Shares(HomogeneousMinTwoTuple):
    def __new__(cls, shares: Sequence[Share]):
        return HomogeneousMinTwoTuple.__new__(cls, shares)

    def is_full_set(self) -> bool:
        return self[0].num_required <= len(set([share['x'] for share in self]))


class Custodian(AttributeDict):
    def __init__(self, name: str, address: str, pubkey: str):
        super().__init__(name=name, address=address, pubkey=pubkey)

    def assign_share(self, share: Share) -> None:
        self['share'] = share

    def receive_share(self, agent: dict, uuid: str) -> None:
        self['share'] = Share(**receive_share(address=self.address, agent=agent, uuid=uuid))


class Custodians(HomogeneousMinTwoTuple):
    def __new__(cls, custodians: Union[Sequence[Custodian], str, IO] = ()):
        def read_file(open_file):
            return load(fp=open_file, object_hook=lambda c: Custodian(**c))

        if isinstance(custodians, (tuple, list)):
            return HomogeneousMinTwoTuple.__new__(cls, custodians)
        elif isinstance(custodians, str) and isfile(custodians):
            with open(custodians, 'r') as infile:
                return HomogeneousMinTwoTuple.__new__(cls, read_file(infile))
        else:
            return HomogeneousMinTwoTuple.__new__(cls, read_file(custodians))

    def assign_shares(self, shares: Shares, transform: Callable[[Share, Custodian], Share] = lambda s: s) -> None:
        run_parallel(func=lambda c, s: c.assign_share(transform(s, c)), func_args_iterable=list(zip(self, shares)))

    def send_shares(self) -> None:
        run_parallel(func=lambda c: send_share(name=c.name, address=c.address, share=dict(c.share)),
                     func_args_iterable=self)

    def request_shares(self, agent: dict, uuid: str) -> None:
        run_parallel(func=lambda c: request_share(name=c.name, address=c.address, agent=agent, uuid=uuid),
                     func_args_iterable=self)

    def receive_shares(self, agent: dict, uuid: str) -> None:
        run_parallel(func=lambda c: c.add_share(agent=agent, uuid=uuid), func_args_iterable=self)

    def dump(self):
        return dumps(self, indent=2)
