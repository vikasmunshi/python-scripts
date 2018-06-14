#!/usr/bin/env python
# -*- coding: utf-8 -*-
from tic_tac_toe import *

__author__ = 'Vikas Munshi'


@mem_cached
def find_center_cell_moves(board):
    return tuple([c for c in get_possible_moves(board) if is_center_cell(c, board.size)])


@mem_cached
def find_corner_cell_moves(board):
    return tuple([c for c in get_possible_moves(board) if is_corner_cell(c, board.size)])


@mem_cached
def find_defensive_moves(board):
    return tuple([c for c in get_possible_moves(board) if last_move_has_won(Board(board.size, board.moves + ((), c)))])


@mem_cached
def find_winning_moves(board):
    return tuple([c for c in get_possible_moves(board) if last_move_has_won(Board(board.size, board.moves + (c,)))])


@mem_cached
def get_moves(board):
    return find_winning_moves(board) or \
           find_defensive_moves(board) or \
           find_corner_cell_moves(board) or \
           find_center_cell_moves(board) or \
           get_possible_moves(board)


@mem_cached
def is_center_cell(cell, board_size) -> bool:
    return cell.row_id not in (0, board_size - 1) and cell.col_id not in (0, board_size - 1)


@mem_cached
def is_corner_cell(cell, board_size) -> bool:
    return cell.row_id in (0, board_size - 1) and cell.col_id in (0, board_size - 1)


def strategy(board):
    return select_random_cell(get_moves(board))
