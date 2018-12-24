#!/usr/bin/env python3
# encoding: utf-8
# ───────────────────────────────── imports ────────────────────────────────── #
import pytest
from kernel import Dungeon
from dungeon_map import Direction, Cell
from random import randint as rdi
# ──────────────────────────────────────────────────────────────────────────── #

n = 20
# ─────────────────────────────── Kernel tests ─────────────────────────────── #
def test_kernel_instanciation():
    for i in range(n):
        d = Dungeon(rdi(2, 20), rdi(2, 20))
        assert d.map.valid()

# ----------------------- string representation tests ------------------------ #
def test_kernel_str():
    d = Dungeon(2, 2, 0)
    print(d)
    assert str(d) == "┌───┬───┐\n│ T │ K │\n├───┼───┤\n│ S │ ◦ │\n└───┴───┘\n"

def test_kernel_agents_str():
    d = Dungeon(2, 2, 1)
    print(d)
    assert str(d) == "┌───┬───┐\n│ T │ K │\n├───┼───┤\n│ S │ ◦*│\n└───┴───┘\n" \
            "*: agent 0's position\n"

def test_kernel_multiple_agents_str():
    d = Dungeon(2, 2, 2)
    d.agents[1].pos = (0, 0)
    print(d)
    assert str(d) == "┌───┬───┐\n│ T^│ K │\n├───┼───┤\n│ S │ ◦*│\n└───┴───┘\n" \
            "*: agent 0's position\n^: agent 1's position\n"

# ------------------------------ moving agents ------------------------------- #
def test_move():
    d = Dungeon(2, 2, 1)
    agent, = d.agents
    assert agent.pos == (1, 1)
    d.move(agent, Direction.NORTH)
    assert agent.pos == (0, 1)
    d.move(agent, Direction.EAST)
    d.move(agent, Direction.EAST)
    d.move(agent, Direction.EAST)
    assert agent.pos == (0, 1)
    d.move(agent, Direction.WEST)
    assert agent.pos == (0, 0)

def test_win():
    d = Dungeon(2, 2, 1)
    a, = d.agents
    d.move(a, Direction.NORTH)
    d.move(a, Direction.WEST)
    d.move(a, Direction.SOUTH)
    d.move(a, Direction.EAST)
    assert d.over == True
