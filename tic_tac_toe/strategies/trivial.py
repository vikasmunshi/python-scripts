#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from tic_tac_toe import *


@cached
def get_move(board: Board) -> Cell:
    return get_free_cells(board)[0]


def strategy(board: Board) -> Cell:
    return get_move(board)
