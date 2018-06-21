#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#   tic_tac_toe/memory.py
import atexit
from json import dump, load
from os.path import exists, splitext

from .types import Board, Cell, Cells, TypeFuncPlay

memory_file = splitext(__file__)[0] + '.json'
memory = []


@atexit.register
def dump_memory() -> None:
    with open(memory_file, 'w') as outfile:
        out = sorted(set(memory))
        dump(out, outfile)


def load_memory() -> None:
    global memory
    if exists(memory_file):
        with open(memory_file, 'r') as infile:
            memory.extend([(tuple(Cell(*m) for m in moves), result) for moves, result in load(infile)])


def persist(moves: Cells, result: str) -> None:
    global memory
    memory.append((moves, result))


def recollect(moves: Cells) -> Cells:
    return tuple({m for m in memory if m[0][:len(moves)] == moves})


def remembered(func: TypeFuncPlay) -> TypeFuncPlay:
    def f(board: Board) -> str:
        r = func(board)
        if r:
            persist(board.moves, r)
        return r

    return f


load_memory()
