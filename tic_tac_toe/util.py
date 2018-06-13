#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#   tic_tac_toe/util.py

from functools import lru_cache
from random import choice

from .types import Cell, Cells

mem_cached = lru_cache(maxsize=None, typed=False)


def select_random_cell(cells: Cells) -> Cell:
    return choice(cells) if cells else None
