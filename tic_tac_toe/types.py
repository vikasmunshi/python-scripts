#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#   tic_tac_toe/types.py

from collections import namedtuple
from typing import Callable, Generator, Tuple, Union

Board = namedtuple('Board', ('size', 'moves'))
Cell = namedtuple('Cell', ('row_id', 'col_id'))
Cell.__repr__ = lambda self: tuple.__repr__(self)
Cells = Tuple[Cell, ...]
Lines = Tuple[Cells, ...]
Player = namedtuple('Player', ('name', 'strategy'))
Player.__repr__ = lambda self: self.name
Players = Tuple[Player, ...]
Score = namedtuple('Score', ('player', 'points', 'wins', 'draws', 'losses', 'games', 'penalties'))
Scores = Tuple[Score, ...]
TypeFunc = Callable[[tuple, dict], str]
TypeFuncPlay = Callable[[Board, Player, Player], str]
TypeTupleOfTuples = Union[Tuple[Tuple, ...], Generator[Tuple[Tuple, ...], None, None]]
