#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#   tic_tac_toe/util.py
from functools import lru_cache
from io import TextIOBase
from random import choice
from sys import stderr

from .types import Cell, Cells, T, TypeFunc

cached = lru_cache(maxsize=None, typed=False)


def logged(func: TypeFunc, log_file: TextIOBase = stderr) -> TypeFunc:
    def f(*args, **kwargs) -> T:
        r = func(*args, **kwargs)
        if func.__name__ == '<lambda>':
            print(r, file=log_file)
        else:
            print('{}{} -> {}'.format(func.__name__, args, r), file=log_file)
        return r

    return f


def select_random_cell(cells: Cells) -> Cell:
    return choice(cells) if cells else None
