#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#   tic_tac_toe/util.py
from functools import lru_cache
from random import choice
from sys import stderr, stdout

from .types import Cell, Cells

cached = lru_cache(maxsize=None, typed=False)


def log_err(*args, **kwargs) -> None:
    print(*args, file=stderr, **kwargs)


def log_msg(*args, **kwargs) -> None:
    print(*args, file=stdout, **kwargs)


def select_random_cell(cells: Cells) -> Cell:
    return choice(cells) if cells else None
