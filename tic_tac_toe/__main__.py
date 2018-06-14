#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#   tic_tac_toe/__main__.py

from argparse import ArgumentParser
from importlib.util import module_from_spec, spec_from_file_location
from inspect import isfunction, signature
from os import listdir
from os.path import dirname, join, splitext
from time import time

from . import Player, Players, Scores, play_tournament, print_to_std_err, strategy


def load_players(players_folder: str, include_bad: bool = False) -> Players:
    expected_signature = signature(strategy)
    for player_file in (file_name for file_name in listdir(players_folder) if file_name.endswith('.py') \
            and not file_name.startswith('_') \
            and (include_bad or not file_name.startswith('bad'))):
        try:
            player_name = splitext(player_file)[0]
            player_strategy_spec = spec_from_file_location(player_name, join(players_folder, player_file))
            player_strategy_module = module_from_spec(player_strategy_spec)
            player_strategy_spec.loader.exec_module(player_strategy_module)
            player_strategy = getattr(player_strategy_module, 'strategy')
            assert isfunction(player_strategy), \
                'strategy is {} and not function'.format(type(player_strategy).__name__)
            assert signature(player_strategy) == expected_signature, \
                'signature is not strategy{}'.format(expected_signature)
            player_author = str(getattr(player_strategy_module, '__author__', 'Anon')).replace(' ', '_')
            yield Player('{}_{}'.format(player_name, player_author), player_strategy)
        except (AssertionError, AttributeError, ImportError, TypeError) as e:
            print_to_std_err('file {} ignored because {}'.format(player_file, str(e)))


def main() -> Scores:
    parser = ArgumentParser(description='Play Tic Tac Toe Tournament')
    parser.add_argument('-d', dest='strategies_folder', type=str, help='location of player strategy files')
    parser.add_argument('-g', dest='games', default=1000, type=int, help='number of games per match, default 1000')
    parser.add_argument('--include_bad', action='store_true', help='include bad* files, ignored by default')
    args = parser.parse_args()
    strategies_folder = args.strategies_folder or join(dirname(__file__), 'strategies')
    return play_tournament(3, args.games, players=tuple(load_players(strategies_folder, args.include_bad)))


if __name__ == '__main__':
    st = time()
    result = main()
    et = time()
    print_to_std_err('Tournament executed in {0:0.4f} seconds\n'.format(et - st))
    longest_name_length = max([len(score.player) for score in result])
    print_str = '{:' + str(longest_name_length + 2) + 's}->{:7d}/{}'
    header_str = '{:' + str(longest_name_length + 2) + 's}-> {}'
    print(header_str.format('Player', 'Points/Matches'))
    for score in result:
        print(print_str.format(score.player, score.points, score.games))