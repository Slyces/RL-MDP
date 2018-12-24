#!/usr/bin/env python3
# encoding: utf-8
# ───────────────────────────────── imports ────────────────────────────────── #
import pytest
from kernel import Dungeon
from random import randint as rdi
# ──────────────────────────────────────────────────────────────────────────── #

n = 20
# ─────────────────────────────── Kernel tests ─────────────────────────────── #
def test_kernel_instanciation():
    for i in range(n):
        d = Dungeon(rdi(2, 20), rdi(2, 20))
        assert d.map.is_valid()

def test_kernel_str():
    d = Dungeon(2, 2)
    assert str(d) == "┌───┬───┐\n│ T │ K │\n├───┼───┤\n│ S │ ◦ │\n└───┴───┘\n"


