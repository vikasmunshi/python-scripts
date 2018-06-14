#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#   tic_tac_toe/types.py

from collections import namedtuple
from typing import Tuple

Board = namedtuple('Board', ['size', 'moves'])
Cell = namedtuple('Cell', ['row_id', 'col_id'])
Cells = Tuple[Cell, ...]
Lines = Tuple[Cells, ...]
Player = namedtuple('Player', ['name', 'strategy'])
Players = Tuple[Player, ...]
Score = namedtuple('Score', ['player', 'points', 'wins', 'draws', 'losses', 'games', 'penalties'])
Scores = Tuple[Score, ...]