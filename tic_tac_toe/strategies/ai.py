#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#   tic_tac_toe/strategies/ai.py
import atexit
from itertools import permutations
from json import dump, load
from os.path import abspath, exists, splitext

from tic_tac_toe.core import get_cells, get_free_cells, last_move_has_won
from tic_tac_toe.memory import recollect, remember
from tic_tac_toe.types import Board, Cell, Cells, Game
from tic_tac_toe.util import cached, select_random_cell


@cached
def reduce_board(board: Board) -> Game:
    for subset_moves in (board.moves[0:n] for n in range(2 * board.size - 1, board.size * board.size + 1)):
        if last_move_has_won(Board(board.size, subset_moves)):
            return Game(moves=subset_moves, result=('O', 'X')[len(subset_moves) % 2])
    return Game(moves=board.moves, result='D')


@cached
def memorize_all_games(size: int) -> None:
    cache_file = abspath(splitext(__file__)[0] + '.{}.json'.format(size))
    if exists(cache_file):
        with open(cache_file, 'r') as infile:
            for g in load(infile): remember(game=Game(moves=tuple(Cell(*c) for c in g[0]), result=g[1]))
    elif size < 4:
        for game in (reduce_board(Board(size, moves)) for moves in permutations(get_cells(Board(size=size, moves=())))):
            remember(game=game)

    def backup() -> None:
        with open(cache_file, 'w') as outfile:
            dump(recollect(moves=()), outfile)

    atexit.register(backup)


def normalize_result(game: Game, player: int) -> int:
    return 1 if game.result == 'D' else 4 if player == len(game.moves) % 2 else -2


@cached
def suggest_moves(board) -> Cells:
    memorize_all_games(board.size)
    num_moves = len(board.moves)
    scores = {}
    for next_move, winner in ((g.moves[num_moves], g.result) for g in recollect(board.moves)):
        if next_move not in scores: scores[next_move] = {'W': 0, 'L': 0, 'D': 0}
        bucket = 'D' if winner == 'D' else 'W' if winner == ('X', 'O')[num_moves % 2] else 'L'
        m = scores[next_move]
        m[bucket] += 1
        m['S'] = int(1000 * (m['W'] + m['D'] * (num_moves % 2) - m['L']) / (m['W'] + m['D'] + m['L']))
    if scores:
        max_score = max(scores.items(), key=lambda x: x[1]['S'])[1]['S']
        return tuple(m[0] for m in scores.items() if m[1]['S'] == max_score)
    return ()


def strategy(board: Board) -> Cell:
    return select_random_cell(suggest_moves(board) or get_free_cells(board))
