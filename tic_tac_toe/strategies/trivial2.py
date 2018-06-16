#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from tic_tac_toe import *


@memoize
def get_move(board):
    return get_possible_moves(board)[0]


def strategy(board):
    return get_move(board)
