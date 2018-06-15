#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from itertools import combinations

from tic_tac_toe import *

__author__ = 'Vikas Munshi'


@cached
def find_center_cell_moves(board: Board) -> Cells:
    return tuple(c for c in get_possible_moves(board) if is_center_cell(c, board.size))


@cached
def find_corner_cell_moves(board: Board) -> Cells:
    return tuple(c for c in get_possible_moves(board) if is_corner_cell(c, board.size))


@cached
def find_defensive_moves(board: Board) -> Cells:
    return tuple(c for c in get_possible_moves(board) if last_move_has_won(Board(board.size, board.moves + ((), c))))


@cached
def find_winning_in_two_moves(board: Board) -> Cells:
    return tuple(i for s in
                 [(m1, m2) for m1, m2 in combinations(get_possible_moves(board), 2)
                  if last_move_has_won(Board(board.size, board.moves + (m1, (), m2)))]
                 for i in s)


@cached
def find_winning_moves(board: Board) -> Cells:
    return tuple(c for c in get_possible_moves(board) if last_move_has_won(Board(board.size, board.moves + (c,))))


@cached
def get_first_move(board: Board) -> Cells:
    return () if not board.moves else find_center_cell_moves(board)


@cached
def get_moves(board: Board) -> Cells:
    return get_first_move(board) or \
           find_winning_moves(board) or \
           find_defensive_moves(board) or \
           find_winning_in_two_moves(board) or \
           find_corner_cell_moves(board) or \
           find_center_cell_moves(board) or \
           recollect_winning_moves(board) or \
           get_possible_moves(board)


@cached
def is_center_cell(cell: Cell, board_size: int) -> bool:
    return cell.row_id not in (0, board_size - 1) and cell.col_id not in (0, board_size - 1)


@cached
def is_corner_cell(cell: Cell, board_size: int) -> bool:
    return cell.row_id in (0, board_size - 1) and cell.col_id in (0, board_size - 1)


def recollect_winning_moves(board: Board) -> Cells:
    next_moves = [g[len(board.moves)] for g in recollect(board.moves)]
    if next_moves:
        return Cell(*max(set(next_moves), key=next_moves.count)),
    return ()


def strategy(board: Board) -> Cell:
    return select_random_cell(get_moves(board))