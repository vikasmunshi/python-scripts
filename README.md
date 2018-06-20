# python-scripts

## Install:

    pip3 install -e git+https://github.com/vikasmunshi/python-scripts.git#egg=akira


## tic_tac_toe

### Usage:

    python3 -m tic_tac_toe [-h] [-d STRATEGIES_FOLDER] [-g GAMES] [-t {fight,points}] [--include_bad] [--py2]
    
    optional arguments:
      -h, --help            show this help message and exit
      -d STRATEGIES_FOLDER  location of player strategy files, default is TIC_TAC_TOE_DIR/strategies
      -g GAMES              number of games per match, default is 1000
      -t {fight,points}     fight for elimination or play for points, default is elimination
      --include_bad         include files matching bad*.py in strategies folder, ignored by default
      --py2                 also load python 2 strategy files

### Template for strategy

    from tic_tac_toe import *
    def strategy(board: Board) -> Cell:
        # your code here
        return Cell(0,0)