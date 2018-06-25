#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#   tic_tac_toe/core.py
from .memory import remembered
from .types import Board, Cell, Cells, Lines, Player
from .util import cached, select_random_cell
from .visualize import show_board, show_game


@cached
def add_move_to_board(board: Board, move: Cell) -> Board:
    return Board(board.size, board.moves + (move,))


@cached
def board_is_full(board: Board) -> bool:
    return not get_free_cells(board)


@cached
def create_empty_board(size: int) -> Board:
    return Board(size, ())


@remembered
@show_board
@cached
def check_winner(board: Board) -> str:
    return ('O', 'X')[len(board.moves) % 2] if last_move_has_won(board) else 'D' if board_is_full(board) else ''


@cached
def get_cells(board: Board) -> Cells:
    return tuple(Cell(row_id, col_id) for row_id in range(board.size) for col_id in range(board.size))


@cached
def get_columns(board: Board) -> Lines:
    return tuple(tuple(Cell(row_id, col_id) for row_id in range(board.size)) for col_id in range(board.size))


@cached
def get_diagonals(board: Board) -> Lines:
    return tuple(Cell(n, n) for n in range(board.size)), tuple(Cell(n, board.size - 1 - n) for n in range(board.size))


@cached
def get_free_cells(board: Board) -> Cells:
    return tuple(cell for cell in get_cells(board) if cell not in board.moves)


@cached
def get_lines(board: Board) -> Lines:
    return get_rows(board) + get_columns(board) + get_diagonals(board)


@cached
def get_moves_of_last_player(board: Board) -> Cells:
    return board.moves[1 - len(board.moves) % 2::2]


@cached
def get_rows(board: Board) -> Lines:
    return tuple(tuple(Cell(row_id, col_id) for col_id in range(board.size)) for row_id in range(board.size))


@cached
def last_move_has_won(board: Board) -> bool:
    return any([all([cell in get_moves_of_last_player(board) for cell in line]) for line in get_lines(board)])


def play(board: Board, one: Player, two: Player) -> str:
    move = one.strategy(board)
    if move not in get_free_cells(board):
        return 'I.{}'.format(one.name)
    return check_winner(add_move_to_board(board, move)) or play(add_move_to_board(board, move), two, one)


@show_game
def play_game(size: int, one: Player, two: Player) -> str:
    return {
        'X': one.name,
        'O': two.name,
        'D': 'D',
        'I.{}'.format(one.name): 'I.{}'.format(one.name),
        'I.{}'.format(two.name): 'I.{}'.format(two.name)

    }[play(create_empty_board(size), one, two)]


def play_game_set(size: int, one: Player, two: Player) -> (str, str):
    return play_game(size, one, two), play_game(size, two, one)


def strategy(board: Board) -> Cell:
    return select_random_cell(get_free_cells(board))
