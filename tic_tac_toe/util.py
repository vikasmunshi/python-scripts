#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#   tic_tac_toe/util.py
from functools import lru_cache
from random import choice
from sys import stderr
from typing import Callable

from .types import Board, Cell, Cells


def log_msg(*args, **kwargs) -> None:
    print(*args, file=stderr, **kwargs)


mem_cached = lru_cache(maxsize=None, typed=False)


def record_final(func: Callable[[Board], str]) -> Callable[[Board], str]:
    def f(board: Board, name: str) -> str:
        r = func(board, name)
        if r:
            print(('D' if r == 'DRAW' else ('O', 'X')[len(board.moves) % 2], board.moves))
        return r

    return f


def select_random_cell(cells: Cells) -> Cell:
    return choice(cells) if cells else None