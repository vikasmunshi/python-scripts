#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#   tic_tac_toe/memory.py

from .types import Board, Game, Games, Moves, TypeFuncBoard

cache = set()


def recollect(moves: Moves) -> Games:
    return tuple(game for game in cache if game.moves[:len(moves)] == moves)


def remember(game: Game) -> None:
    global cache
    if game.result in ('D', 'O', 'X'): cache.add(game)


def remembered(func: TypeFuncBoard) -> TypeFuncBoard:
    global cache

    def f(board: Board) -> str:
        result = func(board)
        if result:
            cache.add(Game(moves=board.moves, result=result))
        return result

    return f
