# python-scripts

## Install:

    pip3 install -e git+https://github.com/vikasmunshi/python-scripts.git#egg=akira


## tic_tac_toe



### Usage:

    python3 -m tic_tac_toe [-h] [-d STRATEGIES_FOLDER] [-g GAMES] [--include_bad]

    optional arguments:
      -h, --help            show this help message and exit
      -d STRATEGIES_FOLDER  location of player strategy files
      -g GAMES              number of games per match, default 1000
      --include_bad         include bad* files, ignored by default
  
### Template for strategy

    from tic_tac_toe import *
    def strategy(board: Board) -> Cell:
        # your code here
        return Cell(0,0)