#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from tic_tac_toe import *

__author__ = 'vm'


def strategy(board: Board) -> Cell:
    return select_random_cell(get_free_cells(board) + (Cell(3, 3),))
