# Tic Tac Toe Tournament

## Install:

    pip3 install -e git+https://github.com/vikasmunshi/python-scripts.git#egg=akira
    or
    git clone https://github.com/vikasmunshi/python-scripts.git
    cd python-scripts
    pip3 install -e tic_tac_toe

## Usage:

    python3 -m tic_tac_toe [-h] [-d STRATEGIES_FOLDER] [-g GAMES] [-t {fight,points}] [--include_bad] [--py2]
    
    optional arguments:
      -h, --help            show this help message and exit
      -d STRATEGIES_FOLDER  location of player strategy files, default is TIC_TAC_TOE_DIR/strategies
      -g GAMES              number of games per match, default is 1000
      -t {fight,points}     fight for elimination or play for points, default is elimination
      --include_bad         include files matching bad*.py in strategies folder, ignored by default
      --py2                 also load python 2 strategy files

  
## Template for player strategy file:

    #!/usr/bin/env python3
    # -*- coding: utf-8 -*-
    from tic_tac_toe import *

    __author__ = 'Your Name'
    
    def strategy(board: Board) -> Cell:
        row_id, col_id = 0, 0
        # your code here
        return Cell(row_id,col_id)
