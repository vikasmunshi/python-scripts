#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tic_tac_toe import *


def strategy(board):
    return select_random_cell(get_free_cells(board))
