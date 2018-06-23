#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#   tic_tac_toe/tournament.py
from .core import play_game_set
from .types import Player, Players, Score, Scores
from .util import count_sub_items, flatten, logged


@logged
def play_match(match_type: str, size: int, num_games: int, players: Players, round_num: int) -> ():
    assert round_num < 256, 'Too many rounds!!!'
    match_func = {'play_match_eliminate': play_match_eliminate, 'play_match_points': play_match_points}[match_type]
    return flatten(match_func(size, num_games, one, two) for n, one in enumerate(players) for two in players[n + 1:])


def play_match_eliminate(size: int, num_games: int, one: Player, two: Player) -> Players:
    results = count_sub_items(play_game_set(size, one, two) for _ in range(num_games // 2))
    draws, wins_one, wins_two, invalid_one, invalid_two, valid_games = tabulate_results(results, one, two)
    return ((one,) if invalid_one or wins_one < wins_two else ()) + \
           ((two,) if invalid_two or wins_two < wins_one else ())


def play_match_points(size: int, num_games: int, one: Player, two: Player) -> Scores:
    results = count_sub_items(play_game_set(size, one, two) for _ in range(num_games // 2))
    draws, wins_one, wins_two, invalid_one, invalid_two, valid_games = tabulate_results(results, one, two)
    return (Score(one.name, wins_one - wins_two - invalid_one, wins_one, wins_two, draws, valid_games, invalid_one),
            Score(two.name, wins_two - wins_one - invalid_two, wins_two, wins_one, draws, valid_games, invalid_two))


def play_tournament_eliminate(size: int, num_games: int, players: Players, round_num: int, rounds: int = 9) -> Players:
    if len(players) <= 1 or round_num > 9:
        return players
    else:
        eliminated = play_match('play_match_eliminate', size, num_games, players, round_num)
        return play_tournament_eliminate(size=size,
                                         num_games=num_games,
                                         players=tuple(player for player in players if player not in eliminated),
                                         round_num=round_num + 1,
                                         rounds=rounds + int(eliminated != 0))


def play_tournament_points(size: int, num_games: int, players: Players) -> Scores:
    results = play_match('play_match_points', size, num_games, players, 1)
    p = {score.player: (0,) * 6 for score in results}
    for s in results:
        p[s.player] = [x + y for x, y in zip(p[s.player], (s.points, s.wins, s.losses, s.draws, s.games, s.penalties))]
    return tuple(sorted([Score(player, *result) for player, result in p.items()], key=lambda r: r.points, reverse=True))


def tabulate_results(results: dict, one: Player, two: Player) -> (int, int, int, int, int, int):
    draws = results.get('D', 0)
    wins_one, wins_two = results.get(one.name, 0), results.get(two.name, 0)
    invalid_one = results.get('I.{}'.format(one.name), 0)
    invalid_two = results.get('I.{}'.format(two.name), 0)
    valid_games = wins_one + wins_two + draws
    return draws, wins_one, wins_two, invalid_one, invalid_two, valid_games
