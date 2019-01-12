#!/usr/bin/env python3
# encoding: utf-8
# ───────────────────────────────── imports ────────────────────────────────── #
import pytest, numpy as np
from kernel import Dungeon
from characters import State
from dungeon_map import Direction, Cell
from random import randint as rdi
# ──────────────────────────────────────────────────────────────────────────── #
np.set_printoptions(precision=5, linewidth=200)

n = 20

pretty_cells = Cell.pretty_cells

b = Cell.start
p = Cell.magic_portal
e = Cell.empty
s = Cell.magic_sword
m = Cell.moving_platform
t = Cell.treasure
k = Cell.golden_key

# ─────────────────────────────── Kernel tests ─────────────────────────────── #
def test_kernel_instanciation():
    for i in range(n):
        d = Dungeon(rdi(2, 20), rdi(2, 20))
        assert d.map.valid()

# ----------------------- string representation tests ------------------------ #
def test_kernel_str():
    if pretty_cells: return
    d = Dungeon(2, 2, 0)
    print(d)
    assert str(d) == "┌───┬───┐\n│ T │ K │\n├───┼───┤\n│ S │ ◉ │\n└───┴───┘\n"

def test_kernel_agents_str():
    if pretty_cells: return
    d = Dungeon(2, 2, 1)
    print(d)
    assert str(d) == "┌───┬───┐\n│ T │ K │\n├───┼───┤\n│ S │ ◉*│\n└───┴───┘\n" \
            "*: agent 0's position\n"

def test_kernel_multiple_agents_str():
    if pretty_cells: return
    d = Dungeon(2, 2, 2)
    d.agents[1].pos = (0, 0)
    print(d)
    assert str(d) == "┌───┬───┐\n│ T^│ K │\n├───┼───┤\n│ S │ ◉*│\n└───┴───┘\n" \
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
    d.move(a, Direction.NORTH)
    d.move(a, Direction.SOUTH)
    d.move(a, Direction.EAST)
    assert d.over == True

def test_transition_portals():
    print('\n' + '=' * 80)
    custom_game = Dungeon(4, 4)

    custom_game.map.load_as_main([t, p, p, s,
                          p, p, m, p,
                          m, p, m, m,
                          k, m, p, b])

    print(custom_game)

    sep = lambda : print('-' * 80)
    sep()
    print('Bottom right, going up gives more chances to get back than going left')
    custom_game.display_transition(State(0, 0, 15), Direction.NORTH)
    custom_game.display_transition(State(0, 0, 15), Direction.WEST)
    sep()
    print('Top left, going down & right are the same.')
    custom_game.display_transition(State(0, 0, 0), Direction.EAST)
    custom_game.display_transition(State(0, 0, 0), Direction.SOUTH)
    print('Going down with key = 1 changes the result states but not their probabilities')
    custom_game.display_transition(State(0, 1, 0), Direction.SOUTH)
    print("Going up with key activates the current cell again and unlocks the treasure")
    custom_game.display_transition(State(0, 1, 0), Direction.NORTH)

def test_tansition_platforms():
    print('\n' + '=' * 80)
    custom_game = Dungeon(4, 3)

    custom_game.map.load_as_main([t, e, s,
                          e, m, e,
                          e, m, e,
                          k, e, b])

    print(custom_game)

    sep = lambda : print('-' * 80)
    sep()
    print("Bottom right, going up is 100% certain")
    custom_game.display_transition(State(0, 0, 11), Direction.NORTH)
    sep()
    print("Top left, going down is 100% certain")
    custom_game.display_transition(State(0, 0, 0), Direction.SOUTH)
    print("Top left, going up with key activates the current cell again and unlocks the treasure")
    custom_game.display_transition(State(0, 1, 0), Direction.NORTH)

    sep()
    print("Middle bottom, going up to a platform")
    custom_game.display_transition(State(1, 1, 10), Direction.NORTH)

def test_policy_agent_long():
    print("=" * 100)
    n, m = 7, 17
    d = Dungeon(n, m)

    i = Cell.start
    v = Cell.empty
    s = Cell.magic_sword
    M = Cell.moving_platform
    p = Cell.magic_portal
    e = Cell.enemy_normal
    w = Cell.wall
    t = Cell.treasure
    k = Cell.golden_key

    d.map.load_as_main(
               [t, k, e, e, e, e, e, e, e, e, e, e, e, e, e, e, e,
                w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, e,
                p, s, v, v, v, v, v, v, v, v, v, v, v, v, v, w, e,
                w, w, w, w, w, w, w, w, w, w, w, w, w, w, v, w, e,
                v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, w, e,
                v, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, e,
                v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, i])

    d.reset()

    T = d.make_transition_matrix()
    R = d.make_reward_matrix(T)
    agent, = d.agents = [PolicyMDP(n - 1, m - 1, n, m, T=T, R=R)]

    agent.setup()

    I = LearningInterface(d)
    I.play_game(0.1)
    assert d.won

def test_value_agent_long():
    print("=" * 100)
    n, m = 7, 17
    d = Dungeon(n, m)

    i = Cell.start
    v = Cell.empty
    s = Cell.magic_sword
    M = Cell.moving_platform
    p = Cell.magic_portal
    e = Cell.enemy_normal
    w = Cell.wall
    t = Cell.treasure
    k = Cell.golden_key

    d.map.load_as_main(
               [t, k, e, e, e, e, e, e, e, e, e, e, e, e, e, e, e,
                w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, e,
                p, s, v, v, v, v, v, v, v, v, v, v, v, v, v, w, e,
                w, w, w, w, w, w, w, w, w, w, w, w, w, w, v, w, e,
                v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, w, e,
                v, w, w, w, w, w, w, w, w, w, w, w, w, w, w, w, e,
                v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, v, i])

    d.reset()

    T = d.make_transition_matrix()
    R = d.make_reward_matrix(T)
    agent, = d.agents = [ValueMDP(n - 1, m - 1, n, m, T=T, R=R)]

    agent.setup()

    I = LearningInterface(d)
    I.play_game(0.1)
    assert d.won 

def test_value_agent_small():
    print("=" * 100)

    n, m = 3, 6
    d = Dungeon(n, m)

    d.map.load_as_main(
              [t, s, p, M, v, k,
               v, v, e, p, w, e,
               v, w, v, v, v, i,])

    d.reset()

    print(d)

    T = d.make_transition_matrix()
    R = d.make_reward_matrix(T)
    agent, = d.agents = [ValueMDP(n - 1, m - 1, n, m, T=T, R=R)]

    agent.setup()

    I = LearningInterface(d)
    I.play_game(0.1)
    assert d.won

def test_value_agent_small():
    print("=" * 100)

    n, m = 3, 6
    d = Dungeon(n, m)

    d.map.load_as_main(
              [t, s, p, M, v, k,
               v, v, e, p, w, e,
               v, w, v, v, v, i,])

    d.reset()

    print(d)

    T = d.make_transition_matrix()
    R = d.make_reward_matrix(T)
    agent, = d.agents = [PolicyMDP(n - 1, m - 1, n, m, T=T, R=R)]

    agent.setup()

    I = LearningInterface(d)
    I.play_game(0.1)
    assert d.won
