#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#   tic_tac_toe/core.py

from collections import Counter

from .types import Board, Cell, Cells, Lines, Player, Players, Score, Scores
from .util import mem_cached, print_to_std_err, select_random_cell


@mem_cached
def add_move_to_board(board: Board, move: Cell) -> Board:
    return Board(board.size, board.moves + (move,))


@mem_cached
def board_is_full(board: Board) -> bool:
    return not get_possible_moves(board)


@mem_cached
def create_empty_board(size: int) -> Board:
    return Board(size, ())


@mem_cached
def check_winner(board: Board, name: str) -> str:
    return name if last_move_has_won(board) else 'DRAW' if board_is_full(board) else ''


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
def get_lines(board: Board) -> Lines:
    return get_rows(board) + get_columns(board) + get_diagonals(board)


@mem_cached
def get_moves_of_last_player(board: Board) -> Cells:
    return board.moves[1 - len(board.moves) % 2::2]


@mem_cached
def get_possible_moves(board: Board) -> Cells:
    return tuple([cell for cell in get_cells(board) if cell not in board.moves])


@mem_cached
def get_rows(board: Board) -> Lines:
    return tuple([tuple([Cell(row_id, col_id) for col_id in range(board.size)]) for row_id in range(board.size)])


@mem_cached
def last_move_has_won(board: Board) -> bool:
    return any([all([cell in get_moves_of_last_player(board) for cell in line]) for line in get_lines(board)])


def play(board: Board, one: Player, two: Player) -> str:
    move = one.strategy(board)
    if move not in get_possible_moves(board): return report_player_made_an_invalid_move(one)
    return check_winner(add_move_to_board(board, move), one.name) or play(add_move_to_board(board, move), two, one)


def play_game(size: int, one: Player, two: Player) -> str:
    return play(create_empty_board(size), one, two)


def play_game_set(size: int, one: Player, two: Player) -> (str, str):
    return play_game(size, one, two), play_game(size, two, one)


def play_match(size: int, num_double_games: int, one: Player, two: Player) -> Scores:
    results = Counter([i for s in (play_game_set(size, one, two) for _ in range(num_double_games)) for i in s])
    wins_one, wins_two, draws = results.get(one.name, 0), results.get(two.name, 0), results.get('DRAW', 0)
    invalid_one = results.get('INVALID{}'.format(one.name), 0)
    invalid_two = results.get('INVALID{}'.format(two.name), 0)
    valid_games = wins_one + wins_two + draws
    return (Score(one.name, wins_one - wins_two - invalid_one, wins_one, wins_two, draws, valid_games, invalid_one),
            Score(two.name, wins_two - wins_one - invalid_two, wins_two, wins_one, draws, valid_games, invalid_two))


def play_tournament(size: int, num_games: int, players: Players) -> Scores:
    opponents = ((one, two) for one in players for two in players if one is not two)
    match_results = [i for s in (play_match(size, num_games // 4, one, two) for one, two in opponents) for i in s]
    r = {score.player: (0,) * 6 for score in match_results}
    for s in match_results:
        r[s.player] = [x + y for x, y in zip(r[s.player], (s.points, s.wins, s.losses, s.draws, s.games, s.penalties))]
    scores = [Score(player, *result) for player, result in r.items()]
    return tuple(sorted(scores, key=lambda s: s.points, reverse=True))


@mem_cached
def report_player_made_an_invalid_move(player: Player) -> str:
    print_to_std_err('Player {} made an invalid move!!!'.format(player.name))
    return 'INVALID{}'.format(player.name)


def strategy(board: Board) -> Cell:
    return select_random_cell(get_possible_moves(board))