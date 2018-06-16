#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#   tic_tac_toe/memory.py
import atexit
from json import dump, load
from os.path import exists, splitext

from .types import Board, Cell, Cells, TypeFuncFinal
from .util import log_err

memory_file = splitext(__file__)[0] + '.txt'
memory = set()


@atexit.register
def dump_memory() -> None:
    with open(memory_file, 'w') as outfile:
        dump(list(memory), outfile)
    log_err('\nDumped {} games from memory to file\n'.format(len(memory)))


def load_memory() -> None:
    global memory
    if exists(memory_file):
        with open(memory_file, 'r') as infile:
            memory.update({tuple(Cell(*m) for m in moves) for moves in load(infile)})
    log_err('\nLoaded {} games from file to memory\n'.format(len(memory)))


def persist(moves: Cells) -> None:
    global memory
    memory.add(moves)


def recollect(moves: Cells) -> Cells:
    return tuple(m for m in memory if m[:len(moves)] == moves)


def remember_winning_games(func: TypeFuncFinal) -> TypeFuncFinal:
    def f(board: Board, name: str) -> str:
        r = func(board, name)
        if r and r != 'DRAW': persist(board.moves)
        return r

    return f


load_memory()
