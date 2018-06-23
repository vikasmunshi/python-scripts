#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#   tic_tac_toe/ai.py
import atexit
import itertools
import json
from os import path
from shutil import copyfile
from string import ascii_lowercase
from typing import Callable, Iterable, Tuple

from .core import create_empty_board as create_empty_namedtuple_board, get_cells as get_namedtuple_cells
from .types import Cell, Cells
from .util import cached as cached_func


@cached_func
def check_board(size: int, all_nine_moves: str) -> Tuple[str, str]:
    for subset_moves in (all_nine_moves[0:n] for n in range(2 * size - 1, size * size + 1)):
        if check_moves_by_one_player(size, subset_moves[0::2]):
            return subset_moves, 'X'
        if check_moves_by_one_player(size, subset_moves[1::2]):
            return subset_moves, 'O'
    return all_nine_moves, 'D'


@cached_func
def check_moves_by_one_player(size: int, player_moves: str) -> bool:
    return any([all([cell in player_moves for cell in line]) for line in get_lines(size)])


@cached_func
def get_all_cells(size: int) -> str:
    return ascii_lowercase[:size * size]


@cached_func
def get_columns(size: int) -> Tuple[str, ...]:
    return tuple(get_all_cells(size)[i::size] for i in range(size))


@cached_func
def get_diagonals(size: int) -> Tuple[str, ...]:
    return tuple(''.join(d) for d in tuple((zip(*[(r[i], r[size - 1 - i]) for i, r in enumerate(get_rows(size))]))))


@cached_func
def get_lines(size: int) -> Tuple[str, ...]:
    return get_rows(size) + get_columns(size) + get_diagonals(size)


@cached_func
def get_rows(size: int) -> Tuple[str, ...]:
    return tuple(''.join(column[i] for column in get_columns(size)) for i in range(size))


@cached_func
def get_map_cell_nt_str(size: int) -> dict:
    return dict(zip(get_namedtuple_cells(create_empty_namedtuple_board(3)), get_all_cells(size)))


@cached_func
def get_map_str_cell_nt(size: int) -> dict:
    return dict(zip(get_all_cells(size), get_namedtuple_cells(create_empty_namedtuple_board(3))))


@cached_func
def map_cells_nt_to_str(size: int, moves: Cells) -> str:
    return ''.join(get_map_cell_nt_str(size)[move] for move in moves)


@cached_func
def map_str_to_cells_nt(size: int, moves: str) -> Cells:
    return tuple(Cell(*get_map_str_cell_nt(size)[move]) for move in moves)


@cached_func
def memorize_all_games(size: int) -> list:
    mem_pickle_file = path.abspath('{}.{}.json'.format(__file__[:-3], size))
    if path.exists(mem_pickle_file):
        with open(mem_pickle_file, 'r') as infile:
            mem_cache = json.load(infile)
    else:
        mem_cache = set()
        for moves, result in yield_all_possible_games(size):
            mem_cache.add(moves)
        mem_cache = sorted(mem_cache)

        def mem_dump() -> None:
            if path.exists(mem_pickle_file):
                copyfile(mem_pickle_file, mem_pickle_file + '.bak')
            with open(mem_pickle_file, 'w') as outfile:
                json.dump(mem_cache, outfile)

        atexit.register(mem_dump)
    return mem_cache


@cached_func
def return_mem_cache_func(size: int) -> Callable[[str], Tuple[str, ...]]:
    mem_cache = memorize_all_games(size)

    def f(moves: str) -> Tuple[str, ...]:
        return tuple(r for r in mem_cache if r.startswith(moves))

    return f


@cached_func
def suggest_moves(board) -> Cells:
    mem_cache_func = return_mem_cache_func(board.size)
    scores = {}
    num_moves = len(board.moves)
    for next_move, winner in ((m[num_moves], check_board(board.size, m)[1])
                              for m in mem_cache_func(map_cells_nt_to_str(board.size, board.moves))
                              if len(m) > num_moves):
        if next_move not in scores: scores[next_move] = {'W': 0, 'L': 0, 'D': 0}
        bucket = 'W' if winner == ('X', 'O')[num_moves % 2] else 'D' if winner == 'D' else 'L'
        nm = scores[next_move]
        nm[bucket] += 1
        nm['S'] = int(1000 * (nm['W'] + nm['D'] * (num_moves % 2) - nm['L']) / (nm['W'] + nm['D'] + nm['L']))
    if scores:
        max_score = max(scores.items(), key=lambda x: x[1]['S'])[1]['S']
        return tuple(map_str_to_cells_nt(board.size, m[0])[0] for m in scores.items() if m[1]['S'] == max_score)
    return ()


def yield_all_possible_games(size: int) -> Iterable[Tuple[str, str]]:
    for p in itertools.permutations(get_all_cells(size)):
        yield check_board(size, ''.join(p))
