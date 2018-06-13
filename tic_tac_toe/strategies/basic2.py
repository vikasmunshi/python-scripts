#!/usr/bin/env python
# -*- coding: utf-8 -*-
from tic_tac_toe import *

__author__ = 'Vikas Munshi'


@memoize
def find_defensive_moves(board):
    return tuple([c for c in get_free_cells(board) if last_player_has_won(Board(board.size, board.moves + ((), c)))])


@memoize
def find_free_center_cells(board):
    return tuple([c for c in get_free_cells(board) if is_center_cell(c, board.size)])


@memoize
def find_free_corners(board):
    return tuple([c for c in get_free_cells(board) if is_corner_cell(c, board.size)])


@memoize
def find_winning_moves(board):
    return tuple([c for c in get_free_cells(board) if last_player_has_won(Board(board.size, board.moves + (c,)))])


@memoize
def get_moves(board):
    return find_winning_moves(board) or \
           find_defensive_moves(board) or \
           find_free_corners(board) or \
           find_free_center_cells(board) or \
           get_free_cells(board)


@memoize
def is_center_cell(cell, board_size):
    return cell.row_id not in (0, board_size - 1) and cell.col_id not in (0, board_size - 1)


@memoize
def is_corner_cell(cell, board_size):
    return cell.row_id in (0, board_size - 1) and cell.col_id in (0, board_size - 1)


def strategy(board):
    return select_random_cell(get_moves(board))
