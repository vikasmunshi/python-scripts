#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#   tic_tac_toe/strategies/ml.py
from operator import itemgetter

from tic_tac_toe.core import get_free_cells, get_lines, last_move_has_won
from tic_tac_toe.types import Board, Cell, Cells, Lines
from tic_tac_toe.util import cached, select_random_cell


@cached
def cost_function(board: Board, move: Cell) -> int:
    b = Board(board.size, board.moves + (move,))
    p = len(b.moves) % 2
    return 1 * count_free_lines(get_lines(b), b.moves[1 - p::2]) - 1 * count_free_lines(get_lines(b), b.moves[p::2])


@cached
def count_free_lines(lines: Lines, moves: Cells) -> int:
    return len(tuple(l for l in lines if not any(m in l for m in moves)))


@cached
def get_costs(board: Board) -> (Cell, int):
    return tuple((move, cost_function(board, move)) for move in get_free_cells(board))


@cached
def get_cost_optimal_moves(board: Board) -> Cells:
    return tuple(c[0] for c in get_costs(board) if c[1] == min(get_costs(board), key=itemgetter(1))[1])


@cached
def get_defensive_moves(board: Board) -> Cells:
    return tuple(c for c in get_free_cells(board) if last_move_has_won(Board(board.size, board.moves + ((), c))))


@cached
def get_winning_moves(board) -> Cells:
    return tuple(c for c in get_free_cells(board) if last_move_has_won(Board(board.size, board.moves + (c,))))


def strategy(board: Board) -> Cell:
    return select_random_cell(get_winning_moves(board) or get_defensive_moves(board) or get_cost_optimal_moves(board))
