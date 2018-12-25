#!/usr/bin/env python3
# encoding: utf-8
# ───────────────────────────────── imports ────────────────────────────────── #
from interface import TextInterface
from kernel import Dungeon
# ──────────────────────────────────────────────────────────────────────────── #

if __name__ == '__main__':
    interface = TextInterface(Dungeon(8, 16, 1))
    winnable = interface.dungeon.winnable
    print('Winnable ??', winnable)
    if winnable:
        print(interface.dungeon.display_paths())
    # interface.loop()
