#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#   tic_tac_toe/core.py

from .types import Board, Cell, Cells, Lines, Player, Players, Score, Scores
from .util import mem_cached, select_random_cell


@mem_cached
def add_move_to_board(board: Board, move: Cell) -> Board:
    return Board(board.size, board.moves + (move,))


@mem_cached
def board_is_full(board: Board) -> bool:
    return not get_free_cells(board)


@mem_cached
def check_winner(board: Board, name: str) -> str:
    return name if last_player_has_won(board) else 'DRAW' if board_is_full(board) else ''


@mem_cached
def create_empty_board(size: int) -> Board:
    return Board(size, ())


@mem_cached
def get_cells(board: Board) -> Cells:
    return tuple([Cell(row_id, col_id) for row_id in range(board.size) for col_id in range(board.size)])


@mem_cached
def get_columns(board: Board) -> Lines:
    return tuple([tuple([Cell(row_id, col_id) for row_id in range(board.size)]) for col_id in range(board.size)])


@mem_cached
def get_diagonals(board: Board) -> Lines:
    return tuple([Cell(n, n) for n in range(board.size)]), \
           tuple([Cell(n, board.size - 1 - n) for n in range(board.size)])


@mem_cached
def get_free_cells(board: Board) -> Cells:
    return tuple([cell for cell in get_cells(board) if cell not in board.moves])


@mem_cached
def get_lines(board: Board) -> Lines:
    return get_rows(board) + get_columns(board) + get_diagonals(board)


@mem_cached
def get_moves_of_last_player(board: Board) -> Cells:
    return board.moves[1 - len(board.moves) % 2::2]


@mem_cached
def get_rows(board: Board) -> Lines:
    return tuple([tuple([Cell(row_id, col_id) for col_id in range(board.size)]) for row_id in range(board.size)])


@mem_cached
def last_player_has_won(board: Board) -> bool:
    return any([all([cell in get_moves_of_last_player(board) for cell in line]) for line in get_lines(board)])


def play(board: Board, one: Player, two: Player) -> str:
    move = one.strategy(board)
    if move not in get_free_cells(board): return 'INVALID MOVE {}'.format(one.name)
    b = add_move_to_board(board, move)
    return check_winner(b, one.name) or play(b, two, one)


def play_1_game(size: int, one: Player, two: Player) -> str:
    return play(create_empty_board(size), one, two)


def play_2_games(size: int, one: Player, two: Player) -> (str, str):
    return play_1_game(size, one, two), play_1_game(size, two, one)


def play_match(size: int, num_double_games: int, one: Player, two: Player) -> Scores:
    winners = [i for s in (play_2_games(size, one, two) for _ in range(num_double_games)) for i in s]
    points = winners.count(one.name) - winners.count(two.name)
    penalties = winners.count('INVALID MOVE {}'.format(one.name)), winners.count('INVALID MOVE {}'.format(two.name))
    valid_games = len(winners) - penalties[0] - penalties[1]
    return Score(one.name, points - penalties[0], valid_games), Score(two.name, - points - penalties[1], valid_games)


def play_tournament(size: int, num_games: int, players: Players) -> Scores:
    opponents = [(one, two) for one in players for two in players if one is not two]
    matches = [i for s in (play_match(size, num_games // 4, one, two) for one, two in opponents) for i in s]
    results = {score.player: [0, 0] for score in matches}
    for score in matches:
        results[score.player][0] += score.points
        results[score.player][1] += score.games
    scores = [Score(player, *result) for player, result in results.items()]
    return tuple(sorted(scores, key=lambda s: s.points, reverse=True))


def strategy(board: Board) -> Cell:
    return select_random_cell(get_free_cells(board))
