#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  vault/transport.py:
#
from json import dump, load
from os import listdir, path, uname

local_cache_dir = u'/usr/local/bin/Vault/cache'


def set_local_cache_dir(local_dir: str) -> None:
    global local_cache_dir
    local_cache_dir = local_dir


def join_local_dir(file_path: str) -> str:
    return path.join(local_cache_dir, file_path)


def list_files(filename_prefix: str) -> list:
    return [join_local_dir(fn) for fn in listdir(local_cache_dir) if fn.startswith(filename_prefix)]


def receive_files(filename_prefix: str, expected_files: int = 0) -> list:
    print('waiting for shares from custodians')
    results = list_files(filename_prefix=filename_prefix)
    if uname()[0] == 'Linux':
        from inotify import constants
        from inotify.adapters import Inotify
        notifier = Inotify()
        notifier.add_watch(path_unicode=local_cache_dir, mask=constants.IN_CLOSE_WRITE)
        events = notifier.event_gen()
        while len(results) < expected_files:
            event = events.__next__()
            if event is not None:
                pathname = event[-2]
                filename = event[-1]
                if filename.startswith(filename_prefix):
                    results.append(path.join(pathname, filename))
                    print('received {} shares'.format(len(results)))
    else:
        from time import sleep
        while len(results) < expected_files:
            results = list_files(filename_prefix=filename_prefix)
            sleep(1)
    return list(results)


def send(sender: str, receiver: str, payload: dict, ) -> None:
    transport_file = path.join(local_cache_dir, '{}_{}.json'.format(receiver, sender))
    with open(transport_file, 'w') as outfile:
        dump(payload, outfile, indent=4)


def request(sender: str, receiver: str, ) -> any:
    transport_file = join_local_dir('{}_{}.json'.format(receiver, sender))
    with open(transport_file, 'w') as infile:
        return load(infile)
