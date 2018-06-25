#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#   tic_tac_toe/__init__.py
from .core import get_cells, get_free_cells, last_move_has_won, strategy
from .tournament import play_tournament_eliminate, play_tournament_points
from .types import Board, Cell, Cells, Player, Players, Scores
from .util import cached, select_random_cell

__package__ = 'tic_tac_toe'
__version__ = '1.4.1'
memoize = cached
__all__ = ['Board', 'Cell', 'Cells', 'Player', 'Players', 'Scores',
           'cached', 'memoize',
           'get_cells', 'get_free_cells', 'last_move_has_won',
           'play_tournament_eliminate', 'play_tournament_points',
           'select_random_cell', 'strategy']
