#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from tic_tac_toe import *

__author__ = 'Vikas Munshi'


@mem_cached
def find_winning_moves(board: Board) -> Cells:
    return tuple([c for c in get_free_cells(board) if last_player_has_won(Board(board.size, board.moves + (c,)))])


@mem_cached
def find_defensive_moves(board: Board) -> Cells:
    return tuple([c for c in get_free_cells(board) if last_player_has_won(Board(board.size, board.moves + ((), c)))])


@mem_cached
def find_free_corners(board: Board) -> Cells:
    corners = (0, board.size - 1)
    return tuple([c for c in get_free_cells(board) if c.col_id in corners and c.row_id in corners])


@mem_cached
def get_center_if_free(board: Board) -> Cell:
    return Cell(1, 1) if Cell(1, 1) in get_free_cells(board) else None


@mem_cached
def get_move(board: Board) -> Cells:
    moves = find_winning_moves(board) or find_defensive_moves(board) or \
           find_free_corners(board) or get_center_if_free(board) or get_free_cells(board)
    return moves


def strategy(board: Board) -> Cell:
    return select_random_cell(get_move(board))
