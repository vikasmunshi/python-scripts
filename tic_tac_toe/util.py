#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#   tic_tac_toe/util.py
from functools import lru_cache
from random import choice
from sys import stderr, stdout
from typing import Callable

from .memory import recollect, remember
from .types import Board, Cell, Cells

cached = lru_cache(maxsize=None, typed=False)


def log_err(*args, **kwargs) -> None:
    print(*args, file=stderr, **kwargs)


def log_msg(*args, **kwargs) -> None:
    print(*args, file=stdout, **kwargs)


recollect = recollect


def record_winning_games(func: Callable[[Board], str]) -> Callable[[Board], str]:
    def f(board: Board, name: str) -> str:
        r = func(board, name)
        if r and r != 'DRAW': remember(board.moves)
        return r

    return f


def select_random_cell(cells: Cells) -> Cell:
    return choice(cells) if cells else None