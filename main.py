#!/usr/bin/env python3
# encoding: utf-8
# ───────────────────────────────── imports ────────────────────────────────── #
from interface import TextInterface, GraphicalInterface
from kernel import Dungeon
# ──────────────────────────────────────────────────────────────────────────── #

if __name__ == '__main__':
    # ─────────────────── print shortest paths if winnable ─────────────────── #
    # interface.dungeon.load_map("default_map.txt")
    # winnable = interface.dungeon.winnable
    # print('Winnable ??', winnable)
    # if winnable:
        # print(interface.dungeon.display_paths())

    # ───────────────────── interactively play the game ────────────────────── #
    # interface = TextInterface(Dungeon(8, 8, 1))
    # interface.loop()

    # ────────────────── interactively play the game in GUI ────────────────── #
    interface = GraphicalInterface(Dungeon(8, 8, 1))
    interface.loop()
