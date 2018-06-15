#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#   tic_tac_toe/__main__.py

from argparse import ArgumentParser
from glob import iglob
from importlib.util import module_from_spec, spec_from_file_location
from inspect import isfunction, signature
from os import environ
from os.path import basename, dirname, join, splitext
from time import time

from . import Player, Players, Scores, log_msg, play_tournament, strategy

environ['COLUMNS'] = '120'


def load_players(players_folder: str, include_bad: bool = False, ignore_signature: bool = False) -> Players:
    expected_signature = signature(strategy)
    for player_file in iglob(join(players_folder, '[!_]*.py')):
        player_name = splitext(basename(player_file))[0]
        try:
            if not include_bad and player_name.startswith('bad'): continue
            player_strategy_spec = spec_from_file_location(player_name, player_file)
            player_strategy_module = module_from_spec(player_strategy_spec)
            player_strategy_spec.loader.exec_module(player_strategy_module)
            player_strategy = getattr(player_strategy_module, 'strategy')
            assert isfunction(player_strategy), \
                'strategy is {} and not function'.format(type(player_strategy).__name__)
            assert ignore_signature or signature(player_strategy) == expected_signature, \
                'signature is not strategy{}'.format(expected_signature)
            player_author = str(getattr(player_strategy_module, '__author__', 'Anon')).replace(' ', '_')
            yield Player('{}_{}'.format(player_name, player_author), player_strategy)
        except (AssertionError, AttributeError, ImportError, SyntaxError, TypeError) as e:
            log_msg('{} ignored because {}'.format(player_name, str(e)))


def main() -> Scores:
    parser = ArgumentParser(description='Play Tic Tac Toe Tournament')
    parser.add_argument('-d', dest='strategies_folder', type=str,
                        help='location of player strategy files, default is TIC_TAC_TOE_DIR/strategies')
    parser.add_argument('-g', dest='games', default=1000, type=int,
                        help='number of games per match, default is 1000')
    parser.add_argument('--include_bad', action='store_true',
                        help='include files matching bad*.py in strategies folder, ignored by default')
    parser.add_argument('--py2', action='store_true',
                        help='also load python 2 strategy files')
    args = parser.parse_args()
    strategies_folder = args.strategies_folder or join(dirname(__file__), 'strategies')
    return play_tournament(3, args.games, players=tuple(load_players(strategies_folder, args.include_bad, args.py2)))


if __name__ == '__main__':
    st = time()
    result = main()
    et = time()
    log_msg('\nTournament executed in {0:0.4f} seconds\n'.format(et - st))
    longest_name_length = max([len(score.player) for score in result])
    msg = '{:' + str(longest_name_length + 2) + 's}{:9d} {:9.2%} {:9d} {:9d} {:9d} {:9d}'
    header_msg = '{:' + str(longest_name_length + 2) + 's}{}'
    log_msg(header_msg.format('Player', '   Points   Wins(%)    Losses     Draws     Games Penalties'))
    for s in result:
        log_msg(msg.format(s.player, s.points, s.wins / (s.games or 1), s.losses, s.draws, s.games, s.penalties))