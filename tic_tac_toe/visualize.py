#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#   tic_tac_toe/visualize.py

from .types import Board, Player, TypeFuncPlay
from .util import cached, printed


def displayed(func: TypeFuncPlay) -> TypeFuncPlay:
    def f(board: Board, one: Player, two: Player) -> str:
        if len(board.moves) == 1:
            show_new_board(one, two)
        update_board(board)
        r = func(board, one, two)
        if r:
            show_result(r)
        return r

    return f


@printed
def show_new_board(one: Player, two: Player) -> str:
    return '\nGame {} vs {}:'.format(one.name, two.name)


@printed
def show_result(r: str) -> str:
    return '\t{}\n'.format(r)


@printed
@cached
def update_board(board: Board) -> str:
    b = '\t\t' + ('____' * board.size + '\n\t\t|' + ' . |' * board.size + '\n\t\t') * board.size + '____' * board.size
    p = tuple(i for i, c in enumerate(b) if c == '.')
    for x, m in ((p[c.col_id + c.row_id * board.size], ('X', 'O')[i % 2]) for i, c in enumerate(board.moves)):
        b = b[:x] + m + b[x + 1:]
    b = b.replace('.', ' ')
    return '\tmove: {} {}\n{}'.format(len(board.moves), board.moves, b)
