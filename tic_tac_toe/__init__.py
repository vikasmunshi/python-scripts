#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#   tic_tac_toe/__init__.py
from .core import Board, Cell, Cells, Player, Players, Scores, get_cells, get_possible_moves, last_move_has_won, \
    play_tournament_eliminate, play_tournament_points, strategy
from .memory import recollect
from .util import cached, log_err, log_msg, select_random_cell

__package__ = 'tic_tac_toe'
__version__ = '1.0.1'
memoize = cached
__all__ = ['Board', 'Cell', 'Cells', 'Player', 'Players', 'Scores',
           'cached', 'memoize',
           'get_cells', 'get_possible_moves',
           'last_move_has_won',
           'play_tournament_eliminate', 'play_tournament_points',
           'log_err', 'log_msg',
           'recollect',
           'select_random_cell', 'strategy']
