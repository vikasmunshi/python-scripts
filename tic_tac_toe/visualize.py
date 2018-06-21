#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#   tic_tac_toe/visualize.py

from .types import Board, Cell, Cells, Player, TypeFuncBoard, TypeFuncGame
from .util import cached, printed


@printed
@cached
def draw_board(board: Board) -> str:
    board_str = draw_empty_board(board.size)
    for marker_position, mark in get_marker_replacements(board.size, board.moves):
        board_str = board_str[:marker_position] + mark + board_str[marker_position + 1:]
    board_str = board_str.replace('.', ' ').replace('\n', '\n\t\t')
    return '\tmove {}: {}\n\t\t{}'.format(len(board.moves), board.moves[-1], board_str)


@cached
def draw_empty_board(size: int) -> str:
    return ('____' * size + '\n|' + ' . |' * size + '\n') * size + '____' * size


@cached
def get_marker_replacements(size: int, moves: Cells) -> ():
    marker_positions = tuple(i for i, c in enumerate(draw_empty_board(size)) if c == '.')
    return tuple((marker_positions[position_num], mark)
                 for position_num, mark in reversed(tuple((c.col_id + c.row_id * size, ('X', 'O')[i % 2])
                                                          for i, c in enumerate(moves) if isinstance(c, Cell)))
                 if position_num < len(marker_positions))


@printed
def new_board(one: Player, two: Player) -> str:
    return '\nGame {} vs {}'.format(one.name, two.name)


@printed
def result(r: str) -> str:
    return 'Score {}\n'.format(r if r != 'D' else 'draw')


def show_board(func: TypeFuncBoard) -> TypeFuncBoard:
    def f(board: Board) -> str:
        draw_board(board)
        return func(board)

    return f


def show_game(func: TypeFuncGame) -> TypeFuncGame:
    def f(size: int, one: Player, two: Player) -> str:
        new_board(one, two)
        r = func(size, one, two)
        result(r)
        return r

    return f
