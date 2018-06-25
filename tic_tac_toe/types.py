#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#   tic_tac_toe/types.py

from collections import namedtuple
from typing import Callable, Generator, Tuple, Union

Board = namedtuple('Board', ('size', 'moves'))
Cell = namedtuple('Cell', ('row_id', 'col_id'))
Cells = Tuple[Cell, ...]
Game = namedtuple('Game', ['moves', 'result'])
Games = Tuple[Game, ...]
Lines = Tuple[Cells, ...]
Moves = Cells
Player = namedtuple('Player', ('name', 'strategy'))
Players = Tuple[Player, ...]
Score = namedtuple('Score', ('player', 'points', 'wins', 'draws', 'losses', 'games', 'penalties'))
Scores = Tuple[Score, ...]
TypeFunc = Callable[[tuple, dict], str]
TypeFuncBoard = Callable[[Board], str]
TypeFuncGame = Callable[[int, Player, Player], str]
TypeTupleOfTuples = Union[Tuple[Tuple, ...], Generator[Tuple[Tuple, ...], None, None]]
