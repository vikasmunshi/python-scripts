#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#   tic_tac_toe/__init__.py
from .core import *
from .memory import recollect

__package__ = 'tic_tac_toe'
__version__ = '1.3.2'
memoize = cached
__all__ = ['Board', 'Cell', 'Cells', 'Player', 'Players', 'Scores',
           'cached', 'memoize',
           'get_cells', 'get_possible_moves',
           'last_move_has_won',
           'play_tournament_eliminate', 'play_tournament_points',
           'recollect',
           'select_random_cell', 'strategy']
