#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#   tic_tac_toe/memory.py
import atexit
from json import dumps, loads
from os.path import exists, splitext

memory_file = splitext(__file__)[0] + '.txt'
memory = set()


@atexit.register
def dump() -> None:
    with open(memory_file, 'w') as outfile:
        outfile.write('\n'.join(dumps(obj) for obj in memory))


def load() -> int:
    global memory
    if exists(memory_file):
        with open(memory_file, 'r') as infile:
            for line in infile.readlines():
                memory.add(tuple(tuple(x) for x in loads(line)))
    return len(memory)


def recollect(obj: tuple) -> tuple:
    return tuple(m for m in memory if m[:len(obj)] == obj)


def remember(obj: tuple) -> None:
    global memory
    memory.add(tuple(tuple(x) for x in obj))


__remembered__ = load()

print('Loaded {} remembered games in memory'.format(__remembered__))