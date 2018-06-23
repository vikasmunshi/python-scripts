#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from tic_tac_toe import Board, Cell
from tic_tac_toe.ai import suggest_moves
from tic_tac_toe.util import select_random_cell

__author__ = 'Vikas Munshi'


def strategy(board: Board) -> Cell:
    return select_random_cell(suggest_moves(board))
