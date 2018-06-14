#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#   tic_tac_toe/util.py
from functools import lru_cache
from random import choice
from sys import stderr

from .types import Cell, Cells

mem_cached = lru_cache(maxsize=None, typed=False)


def print_to_std_err(*args, **kwargs) -> None:
    print(*args, file=stderr, **kwargs)


def select_random_cell(cells: Cells) -> Cell:
    return choice(cells) if cells else None