#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from tic_tac_toe import *

__author__ = 'Vikas Munshi'


@mem_cached
def find_defensive_moves(board: Board) -> Cells:
    return tuple([c for c in get_free_cells(board) if last_player_has_won(Board(board.size, board.moves + ((), c)))])


@mem_cached
def find_free_center_cells(board: Board) -> Cells:
    return tuple([c for c in get_free_cells(board) if is_center_cell(c, board.size)])


@mem_cached
def find_free_corners(board: Board) -> Cells:
    return tuple([c for c in get_free_cells(board) if is_corner_cell(c, board.size)])


@mem_cached
def find_winning_moves(board: Board) -> Cells:
    return tuple([c for c in get_free_cells(board) if last_player_has_won(Board(board.size, board.moves + (c,)))])


@mem_cached
def get_moves(board: Board) -> Cells:
    return find_winning_moves(board) or \
           find_defensive_moves(board) or \
           find_free_corners(board) or \
           find_free_center_cells(board) or \
           get_free_cells(board)


@mem_cached
def is_center_cell(cell: Cell, board_size: int) -> bool:
    return cell.row_id not in (0, board_size - 1) and cell.col_id not in (0, board_size - 1)


@mem_cached
def is_corner_cell(cell: Cell, board_size: int) -> bool:
    return cell.row_id in (0, board_size - 1) and cell.col_id in (0, board_size - 1)


def strategy(board: Board) -> Cell:
    return select_random_cell(get_moves(board))
