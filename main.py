#!/usr/bin/env python3
# encoding: utf-8
# ───────────────────────────────── imports ────────────────────────────────── #
from interface import TextInterface
from kernel import Dungeon
# ──────────────────────────────────────────────────────────────────────────── #

if __name__ == '__main__':
    interface = TextInterface(Dungeon(4, 6, 1))
    interface.loop()
