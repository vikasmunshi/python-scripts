#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#   tic_tac_toe/__init__.py
from .core import (Board, Cell, Cells, Player, Players, Scores,
                   mem_cached,
                   get_cells, get_free_cells,
                   last_player_has_won,
                   play_match, play_tournament,
                   select_random_cell, strategy)

__package__ = 'tic_tac_toe'
__version__ = '1.0.0'
memoize = mem_cached
__all__ = ['Board', 'Cell', 'Cells', 'Player', 'Players', 'Scores',
           'mem_cached', 'memoize',
           'get_cells', 'get_free_cells',
           'last_player_has_won',
           'play_match', 'play_tournament',
           'select_random_cell', 'strategy']
