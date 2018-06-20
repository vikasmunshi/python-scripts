#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from tic_tac_toe import *

__author__ = 'Vikas Munshi'


@cached
def find_defensive_moves(board: Board) -> Cells:
    return tuple(c for c in get_possible_moves(board) if last_move_has_won(Board(board.size, board.moves + ((), c))))


@cached
def find_winning_in_two_moves(board: Board) -> Cells:
    return tuple(i for s in
                 [(m1, m2) for n, m1 in enumerate(get_possible_moves(board)) for m2 in get_possible_moves(board)[n + 1:]
                  if last_move_has_won(Board(board.size, board.moves + (m1, (), m2)))]
                 for i in s)


@cached
def find_winning_moves(board: Board) -> Cells:
    return tuple(c for c in get_possible_moves(board) if last_move_has_won(Board(board.size, board.moves + (c,))))


def get_moves(board: Board) -> Cells:
    return find_winning_moves(board) or \
           find_defensive_moves(board) or \
           recollect_winning_move(board) or \
           get_possible_moves(board)

@cached
def recollect_winning_move(board: Board) -> Cells:
    next_moves = [g[len(board.moves)] for g in recollect_decided(board.moves)]
    if next_moves:
        return Cell(*max(set(next_moves), key=next_moves.count)),
    return ()


def strategy(board: Board) -> Cell:
    return Cell(1, 1) if not board.moves else select_random_cell(get_moves(board))
