#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#   tic_tac_toe/util.py
from collections import Counter
from functools import lru_cache
from io import TextIOBase
from random import choice
from sys import stderr

from .types import Cell, Cells, TypeFunc, TypeTupleOfTuples

cached = lru_cache(maxsize=None, typed=False)


def count_sub_items(l: TypeTupleOfTuples) -> dict:
    return Counter([i for s in l for i in s])


def flatten(l: TypeTupleOfTuples) -> (tuple, ...):
    return tuple([i for s in l for i in s])


def logged(func: TypeFunc, log_file: TextIOBase = stderr) -> TypeFunc:
    def f(*args, **kwargs) -> str:
        r = func(*args, **kwargs)
        if func.__name__ == '<lambda>':
            print('msg ->', r, file=log_file)
        else:
            print('{} ({}) -> {}'.format(func.__name__, ', '.join(str(arg) for arg in args), r), file=log_file)
        return r

    return f


def printed(func: TypeFunc, log_file: TextIOBase = stderr) -> TypeFunc:
    def f(*args, **kwargs) -> str:
        r = func(*args, **kwargs)
        print(r, file=log_file)
        return r

    return f


def select_random_cell(cells: Cells) -> Cell:
    return choice(cells) if cells else None
