#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#   tic_tac_toe/memory.py
import atexit
from json import dump, load
from os.path import exists, splitext

from .types import Board, Cell, Cells, TypeFuncFinal, TypeMemItem
from .util import log_msg

__memory_file__ = splitext(__file__)[0] + '.json'
__memory__ = set()


@atexit.register
def dump_memory() -> None:
    with open(__memory_file__, 'w') as outfile:
        dump(list(__memory__), outfile)
        # log_msg('Dumped {} winning games from memory to file'.format(len(memory)))


def load_memory() -> None:
    global __memory__
    if exists(__memory_file__):
        with open(__memory_file__, 'r') as infile:
            __memory__.update([tuple_of_moves(m) for m in load(infile)])
    log_msg('Loaded {} winning games from file to memory'.format(len(__memory__)))


def persist(moves: Cells) -> None:
    global __memory__
    __memory__.add(tuple_of_moves(moves))


def recollect(moves: Cells) -> Cells:
    return tuple(Cell(*m) for m in __memory__ if m[:len(moves)] == tuple_of_moves(moves))


def remember_winning_games(func: TypeFuncFinal) -> TypeFuncFinal:
    def f(board: Board, name: str) -> str:
        r = func(board, name)
        if r and r != 'DRAW': persist(board.moves)
        return r

    return f


def tuple_of_moves(moves: Cells) -> TypeMemItem:
    return tuple(tuple(c) for c in moves)


load_memory()
