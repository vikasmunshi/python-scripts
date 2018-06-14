# Tic Tac Toe Tournament

## Install:

    pip3 install -e git+https://github.com/vikasmunshi/python-scripts.git#egg=akira
    or
    git clone https://github.com/vikasmunshi/python-scripts.git
    cd python-scripts
    pip3 install -e tic_tac_toe

## Usage:

    python3 -m tic_tac_toe [-h] [-d STRATEGIES_FOLDER] [-g GAMES] [--include_bad]

    optional arguments:
      -h, --help            show this help message and exit
      -d STRATEGIES_FOLDER  location of player strategy files
      -g GAMES              number of games per match, default 1000
      --include_bad         include bad* files, ignored by default
  
## Template for player strategy file:

    #!/usr/bin/env python3
    # -*- coding: utf-8 -*-
    from tic_tac_toe import *

    __author__ = 'Your Name'
    
    def strategy(board: Board) -> Cell:
        row_id, col_id = 0, 0
        # your code here
        return Cell(row_id,col_id)
