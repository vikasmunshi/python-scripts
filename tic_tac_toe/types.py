#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#   tic_tac_toe/types.py

from collections import namedtuple
from typing import Callable, Tuple, TypeVar

Board = namedtuple('Board', ['size', 'moves'])
Cell = namedtuple('Cell', ['row_id', 'col_id'])
Cells = Tuple[Cell, ...]
Lines = Tuple[Cells, ...]
Player = namedtuple('Player', ['name', 'strategy'])
Player.__repr__ = lambda self: self.name
Players = Tuple[Player, ...]
Score = namedtuple('Score', ['player', 'points', 'wins', 'draws', 'losses', 'games', 'penalties'])
Scores = Tuple[Score, ...]
T = TypeVar('T')
TypeFunc = Callable[..., T]
TypeFuncFinal = Callable[[Board], str]
TypeMemItem = Tuple[Tuple, ...]
