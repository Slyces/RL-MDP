#!/usr/bin/env python3
# encoding: utf-8
# ───────────────────────────────── imports ────────────────────────────────── #
from interface import TextInterface, GraphicalInterface
from mdp import *
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

    # ────────────────────────── trying default map ────────────────────────── #
    # n, m = 2, 2
    # dungeon = Dungeon(n, m, 1, [ValueMDP])

    # dungeon.load_map('default_map.txt')

    # interface = TextInterface(dungeon)
    # interface.play_game()
