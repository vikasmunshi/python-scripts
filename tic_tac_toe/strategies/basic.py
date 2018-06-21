#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from tic_tac_toe import *

__author__ = 'Vikas Munshi'


@cached
def find_defensive_moves(board: Board) -> Cells:
    return tuple(c for c in get_possible_moves(board) if last_move_has_won(Board(board.size, board.moves + ((), c))))


@cached
def find_winning_moves(board: Board) -> Cells:
    return tuple(c for c in get_possible_moves(board) if last_move_has_won(Board(board.size, board.moves + (c,))))


def get_moves(board: Board) -> Cells:
    return find_winning_moves(board) or \
           find_defensive_moves(board) or \
           recollect_winning_move(board) or \
           get_possible_moves(board)


def recollect_winning_move(board: Board) -> Cells:
    def eval_score(m: dict) -> float:
        return ((m['wins'] - m['draws']) ^ 2) / m['count']

    win_mark = ('X', 'O')[len(board.moves) % 2]
    move_num = len(board.moves)
    moves = tuple((moves[move_num], result) for moves, result in recollect(board.moves))
    if moves:
        scores = {move[0]: {'count': 0, 'wins': 0, 'losses': 0, 'draws': 0} for move in moves}
        for move, result in moves:
            scores[move]['count'] += 1
            scores[move]['wins'] += 1 if result == win_mark else 0
            scores[move]['losses'] += 1 if result != 'D' and result != win_mark else 0
            scores[move]['draws'] += 1 if result == 'D' else 0
            scores[move]['score'] = eval_score(scores[move])

        winning_moves = tuple(filter(lambda m: m[1]['wins'] > 0 and m[1]['losses'] == 0, scores.items()))
        if winning_moves:
            return max(winning_moves, key=lambda m: m[1]['score'])[0],
    return ()


def strategy(board: Board) -> Cell:
    return select_random_cell(get_moves(board) or get_possible_moves(board))
