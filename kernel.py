#!/usr/bin/env python3
# encoding: utf-8
# ───────────────────────────────── imports ────────────────────────────────── #
from random import random
from markov import MarkovChain
from characters import Adventurer, AdventurerLearning,State
from dungeon_map import DungeonMap, Direction, Cell, AStar
import utils, numpy as np
# ──────────────────────────────────────────────────────────────────────────── #
# @TODO (for the indian coding team) visualize a policy

# ────────────── Kernel classes for the MADI project (01/2019) ─────────────── #
class Dungeon(object):
    """ Dungeon object containing all the game logic """

    p_enemy = 0.7

    def __init__(self, n: int, m: int, nb_players: int = 1, player_classes: list= None):
        self.n, self.m = n, m
        State.configure(self.n, self.m)
        self.map = DungeonMap(n, m)
        while not self.winnable:
            self.map = DungeonMap(n, m)
        assert len(player_classes) >= nb_players
        self.last_actions = [None for i in range(nb_players)]
        self.over, self.won = False, False
        self.caption = ''

        self.teleport_distributions = {}

        player_classes = [AdventurerLearning for i in range(nb_players)] \
                if player_classes is None else player_classes
        self.agents = [pclass(self) for pclass in player_classes[:nb_players]]

        State.configure(n, m)

    # ─────────── display a transition matric in a readable output ─────────── #
    def display_transition(self, s: State, a: Direction):
        """
        Displays a transition for a given state and action
        """
        arr = ['↑', '→', '↓', '←'][a.to_int]
        print('{s},{arr}:'.format(s=s, arr=arr))
        tr = self.make_transition_matrix()[s.id, a.to_int]
        for (i, p) in enumerate(tr):
            if p > 0:
                print('- {p:4.2%}: {st}'.format(p=p, st=State(s_id=i)))

    # ───────────────────────── add agent post init ────────────────────────── #
    def add_agent(self, agent: Adventurer):
        self.agents.append(agent)

    # ──────────────────── constructing the reward matrix ──────────────────── #
    def make_reward_matrix(self, T: np.array):
        """
        The reward matrix is quite simple:
            - death → (*,*,*) : -1
            - (*,0,*) → (*,1,*) take key : 1
            - (*,1,*) → (*,2,*) take treasure : 1
            - (*,2,start) → (*,2,start) : 1
            - else, 0
        Negative reward for death
        Positive reward for (actually) picking up the key, picking up the treasure
        and returning to start with the treasure
        """
        n, m = self.n, self.m
        n_state = State.max_id + 1
        death = n_state - 1
        R = np.zeros((n_state, 4), np.float64)
        for sw in range(2):
            for tr in range(3):
                for p in range(n * m):
                    s = State(sw, tr, p)
                    for a in Direction:
                        # we only reward 'certain' actions, actions with
                        # probability 1 to lead to a state
                        if np.amax(T[s.id, a.to_int]) == 1:
                            certain_state = np.argmax(T[s.id, a.to_int])
                            st = State(s_id=certain_state) # target state
                            # -------------- (*,0,*) → (*,1,*) --------------- #
                            #                             
                            if s.treasure == 0 and st.treasure == 1:
                                R[s.id, a.to_int] = 0.5
                            # -------------- (*,1,*) → (*,2,*) --------------- #
                            #                            ﰤ 
                            if s.treasure == 1 and st.treasure == 2:
                                R[s.id, a.to_int] = 0.5
                            # ---------- (*,2,start) → (*,2,start) ----------- #
                            if s.treasure == st.treasure == 2 and \
                                    s.position == st.position == n * m - 1:
                                R[s.id, a.to_int] = 1
                            # ---------------- death → death ----------------- #
                            if s.id == st.id == death:
                                R[s.id, a.to_int] = -1
        return R

    # ────────────────── constructing the transition matrix ────────────────── #
    def make_transition_matrix(self):
        """
        Creates the complete transition matrix, including every possible state
        and action, and the transition from one to another.

        Contains all the possible values of T(s, a, s'), the probability to go
        from s to s' by doing a.
        """
        n_states = State.max_id + 1 # last state is death
        n, m = self.n, self.m
        T = np.zeros((n_states, 4, n_states), np.float64)
        S = self.markov_chain()
        M = self.moving_markov_chain()
        # ────────────────────────── for each state ────────────────────────── #
        for sw in range(2):
            for tr in range(3):
                for p in range(n * m):
                    i, j = p // m, p % m
                    s = State(sw, tr, p)
                    cell = self.map[i, j]
                    # ───────── find the transitions from that state ───────── #
                    if cell == Cell.magic_portal or cell == Cell.moving_platform:
                        transitions = self.special_transition(S, M, s)
                    else:
                        transitions = S[s.id, :]
                    # ─────── find the state - actions that lead to it ─────── #
                    for ((k, l), direction) in self.map.neighbors(i, j):
                        # if (k,l) is ↑ of (i, j), (i, j) is ↓ of (k, l)
                        s.position = k * m + l
                        reverse_dir = direction.reverse
                        T[s.id, reverse_dir.to_int, :] = transitions
        # ─────────── any action not yet found is to stay inplace ──────────── #
        for sid in range(n_states):
            for a in Direction:
                s = State(s_id=sid)
                if sum(T[s.id, a.to_int]) == 0:
                    mu = np.zeros(n_states, np.float64)
                    mu[s.id] = 1
                    T[s.id, a.to_int, :] = S.iterate(mu)
        return T

    # ──────────────── handling moving platforms and portals ───────────────── #
    def special_transition(self, S: MarkovChain, M: MarkovChain, state: State):
        """
        @param S: Markovchain= a markov chain representing the stable states of
                  the dungeon, i.e. the states that must only be iterated once
                  ex: the 'over an ennemy cell' state. that state might lead to
                  itself, and yet you won't fight the ennemy again.
                  this markov chain must only be used to advance of 1 time step.

                  it contains every actual states of the game, including the
                  'death' state.

        @param M: Markochain= a markov chain representing the 'moving states' of
                  the dungeon, i.e. the states that can be recursive. those
                  states, such as the moving platform and the portal, are just
                  temporary. they lead you to another stable state, or to
                  another moving state that will lead you back elsewhere. they
                  can be infinitely cycling between themselves.
                  To deal with such states, we need to iterate a markov chain
                  until we reach stable probabilities, i.e. probabilities over
                  the states that are unchanged upon iteration of the markov
                  chain.

                  To simplify this, as the two cells considered here only impact
                  the position on the grid, we use a reduced version of the
                  states, only including n * m states (the grid positions).

                  The result obtained at stability is the probability to be in
                  each cell of the dungeon, after using a moving platform or
                  teleporter. It accounts for every recursive teleportation
                  that can occur.

        @param state: State= the particular state to be computed. It must be
                  a state where the position corresponds to a 'moving cell'.

        This function deals with two difficult or 'special' states, the portal
        and the moving platform. They teleport the player to another cell, that
        is then triggered as if the player just walked into it. If that state is
        a portal or moving platform, the result is recursive and might lead again
        to a teleportation, effectively creating possible infinite loop.

        To deal with such states, we use two markov chains. One considering stable
        states, that must be iterated only once, and one for the recursive states
        that is iterated until we find a correct probability distribution.

        Ad this methods operates with heavy matrix operations that might be
        needed multiple times, we store the results of already computed calculations
        to reuse them and modify them according to the need.
        """
        # This method will be heavily commented
        n, m = self.n, self.m

        # ──────────── extracting the grid position of the state ───────────── #
        p = state.position

        # ────────────── checking that the state given is valid ────────────── #
        assert self.map[p] in (Cell.magic_portal, Cell.moving_platform)

        # ────────────────── checking for existing results ─────────────────── #
        distrib = np.zeros(n * m, np.float64)
        if p in self.teleport_distributions:
            distrib = self.teleport_distributions[p]
        # ─────────────── compute the results if not available ─────────────── #
        else:
            # Create a probability vector where we are in p
            mu = np.zeros(n * m, np.float64)
            mu[p] = 1
            distrib = M.convergence_iteration(mu)
            self.teleport_distributions[p] = distrib
        assert distrib.shape == (n * m,) and abs(sum(distrib) - 1) < 10e-6

        # ───────────────── convert grid positions to state ────────────────── #
        # We now have the distribution over the grid position. However, we need
        # a distribution over the real state of the game, accounting for items.
        # As the special cells do not impact (yet) items, we just need to 
        # put this vector at the right place in the (6 times) larger state vector
        # of the dungeon.
        padding = state.sword * 3 + state.treasure
        block_size = n * m

        transition = np.zeros(State.max_id + 1, np.float64)
        transition[padding * block_size: (padding + 1) * block_size] = distrib

        # ───── iterate once the new states over the rest of the dungeon ───── #
        transition = S.iterate(transition, 1)
        assert abs(sum(transition) - 1) < 10e-5
        return transition

    # ──────────────────── constructing the markov chain ───────────────────── #
    def markov_chain(self):
        n_state = State.max_id + 1 # because max id is n - 1
        M = np.zeros((n_state, n_state), np.float64)
        n, m = self.n, self.m
        death = n_state - 1
        M[death, death] = 1
        for sw in range(2):
            for tr in range(3):
                for p in range(n * m):
                    i, j = p // m, p % m
                    cell = self.map[i, j]
                    state = State(sw, tr, p)
                    index = state.id
                    # ────────────── empty cell : stay inplace ─────────────── #
                    if cell == Cell.empty or cell == Cell.start:
                        M[index, index] = 1
                    # ───────────── wall : bounce back to start ────────────── #
                    if cell == Cell.wall:
                        state.position = n * m - 1
                        M[index, state.id] = 1
                    # ──────────────── crack : kill instantly ──────────────── #
                    if cell == Cell.crack:
                        M[index, death] = 1
                    # ──────────────────── ennemy : fight ──────────────────── #
                    if cell == Cell.enemy_normal and state.sword:
                        M[index, index] = 1 # fight won
                    if cell == Cell.enemy_normal and not state.sword:
                        M[index, index] = 1 - Dungeon.p_enemy
                        M[index, death] = Dungeon.p_enemy
                    # ───────── political enemy : do not use a sword ───────── #
                    if cell == Cell.enemy_special and not state.sword:
                        M[index, index] = 1 # not dangerous when weaponless
                    if cell == Cell.enemy_special and state.sword:
                        M[index, index] = 1 - Dungeon.p_enemy
                        M[index, death] = Dungeon.p_enemy
                    # ─────────────── magic sword acquisition ──────────────── #
                    if cell == Cell.magic_sword:
                        state.sword = 1
                        M[index, state.id] = 1
                    # ─────────────────── key acquisition ──────────────────── #
                    if cell == Cell.golden_key:
                        state.treasure = max(state.treasure, 1)
                        # get the key if you didn't have it, else keep the treasure
                        M[index, state.id] = 1
                    # ───────────────── treasure acquisition ───────────────── #
                    if cell == Cell.treasure:
                        state.treasure = 2 if state.treasure >= 1 else 0
                        M[index, state.id] = 1
                    # ─────── trap : back to start, death, or nothing ──────── #
                    if cell == Cell.trap:
                        M[index, index] = 0.6 # nothing happens
                        state.position = n * m - 1
                        M[index, state.id] = 0.3 # tunnel to start
                        M[index, death] = 0.1 # death
                    if cell == Cell.magic_portal or cell == Cell.moving_platform:
                        M[index, index] = 1
        return MarkovChain(M)

    def moving_markov_chain(self):
        """
        Creates a markov chain with grid cells as states, to determine the
        probability to be in a state when using a recurrent transition (portal,
        moving-platform)
        """
        n, m = self.n, self.m
        n_state = n * m
        M = np.zeros((n_state, n_state), np.float64)
        for p in range(n * m):
            i, j = p // m, p % m
            cell = self.map[i, j]
            if cell == Cell.moving_platform:
                valid_neighbors = self.map.all_cell_dist((i, j), 1)
                for (k, l) in valid_neighbors:
                    p_next = k * m + l
                    M[p, p_next] = 1 / len(valid_neighbors)
            elif cell == Cell.magic_portal:
                valid_cells = self.map.all_cell_dist((i, j), -1)
                for (k, l) in valid_cells:
                    p_next = k * m + l
                    M[p, p_next] = 1 / len(valid_cells)
            else:
                M[p, p] = 1
        return MarkovChain(M)

    # ────────────────────── is that dungeon winnable ? ────────────────────── #
    @property
    def winnable(self):
        """ getter for winnable attribute """
        return self.map.winnable

    # ──────────────────────────── moving agents ───────────────────────────── #
    def move(self, agent: Adventurer, direction: Direction):
        """
        Moves an agent in a direction

        @return an int, the reward associated with this action in that state
        """
        self.last_actions[self.agents.index(agent)] = direction
        agent.pos = self.map.move(agent.pos, direction)
        return self.enter(agent, self.map[agent.pos])

    def teleport(self, agent: Adventurer, position: (int, int)):
        """ Teleports an agent to a given position (might be usefull for animations)"""
        i, j = position
        assert 0 <= i < self.n and 0 <= j < self.m, "can't teleport outside of the dungeon"
        assert self.map[position] != Cell.wall, "can't teleport in a wall"
        agent.pos = position
        self.caption += '\n'
        return self.enter(agent, self.map[agent.pos])

    # ─────────────────────────── entering a cell ──────────────────────────── #
    def enter(self, agent: Adventurer, cell: Cell):
        """
        Performs the most simple cells tasks, and delegates to appropriate
        functions if needed

        @return an int representing the reward of the move
        """
        # assert cell != Cell.wall, "wall cells should never be entered"
        sword = agent.has_item(Cell.magic_sword)
        # -------------- walls bounce back to starting position -------------- #
        if cell == Cell.wall:
            self.caption += "Bounced against a wall ... Back to start !"
            return self.teleport(agent, (self.n - 1, self.m - 1))
        # ---------------- items are treated in the same way ----------------- #
        elif cell == Cell.golden_key or cell == Cell.magic_sword:
            if agent.has_item(cell):
                self.caption += "Can't pick up another {}, already have one".format(cell.name)
            else:
                self.caption += "Picked up an item ({}) !!".format(cell.name)
                agent.acquire_item(cell)
                if cell == Cell.golden_key: return 0.5
                else: return 0
        # ------------------ treasure is particular, though ------------------ #
        elif cell == Cell.treasure and agent.has_item(Cell.golden_key):
            self.caption += "Got the treasure !"
            agent.acquire_item(cell)
            return 0.5
        # ------------ magic portal and moving platforms teleport ------------ #
        elif cell == Cell.magic_portal:
            valid_cell = self.map.random_cell_dist()
            self.caption += "STARGAAAATE : {} → {}".format(agent.pos, valid_cell)
            return self.teleport(agent, valid_cell)
        elif cell == Cell.moving_platform:
            valid_neighbor = self.map.random_cell_dist(agent.pos, 1)
            (nx, ny), (x, y) = valid_neighbor, agent.pos
            self.caption += "Woops ! It moves ! (teleported to {})".format(Direction((nx - x, ny - y)).name)
            return self.teleport(agent, valid_neighbor) # adjacent cell <=> Manhattan dist of 1
        # ---------------------- oh, CRACK, you're dead ---------------------- #
        elif cell == Cell.crack:
            self.caption += "DAMN ! CRACK !!! I'm dead."
            self.kill(agent)
        # ----------------------- care, it's a trap !! ----------------------- #
        elif cell == Cell.trap:
            p = random() # random floating number in [0, 1[
            self.caption += "ITS A TRAPPP "
            if p < 0.1:
                self.caption += "I'm dead."
                self.kill(agent) # 10% : death
            elif p < 0.4:
                self.caption += "Back to start. (tunneled :] )"
                return self.teleport(agent, (self.n - 1, self.m - 1)) # 30% : back to start
            else:
                self.caption += "But it's ineffective."
            # 60% : nothing
        # ----------------------------- FIGHT !! ----------------------------- #
        # -------------------- normal enemy (use a sword) -------------------- #
        elif cell == Cell.enemy_normal and not sword:
            # no fight for the brave wielding a sword
            self.caption += "Enemy in sight ! "
            p = random() # random floating number in [0, 1[
            if p < Dungeon.p_enemy: # the player is victorious (p_enemy)%
                self.caption += "Easily defeated."
            else:
                self.caption += "Woops, I'm dead"
                self.kill(agent)
        elif cell == Cell.enemy_normal and sword:
            self.caption += "BIM ! BAM ! MAGIC SWORD IN YOUR FACE !"
        # -------------------------- special enemy --------------------------- #
        elif cell == Cell.enemy_special and not sword:
            # don't fight
            self.caption += "Not a threat for me."
        elif cell == Cell.enemy_special and sword:
            self.caption += "This enemy can't be slain ! "
            p = random()  # random floating number in [0, 1[
            if p > Dungeon.p_enemy:  # the player is victorious (p_enemy)%
                self.caption += "I managed to flee."
            else:
                self.caption += "Goodbye, sweet world"
                self.kill(agent)
        # ------------ returning to the start (with the treasure) ------------ #
        elif cell == Cell.start and agent.has_item(Cell.treasure):
            self.caption += "I WON. !!!"
            self.victory(agent)
            return 1

        # ───────────── handle the reward in various situations ────────────── #
        return -1 if not agent.alive else 0

    # ────────────────────────────────── Reset ─────────────────────────────── #
    def reset(self):
        self.map.reset()
        self.last_actions = [None for x in self.agents]
        State.configure(self.n, self.m)
        self.caption = ''
        self.over, self.won = False, False
        for agent in self.agents:
            agent.n, agent.m = self.n, self.m
            agent.reset()

    def load_map(self, path: str):
        self.map.load_map(path)
        self.m, self.n = self.map.m, self.map.n
        self.reset()

    def save_map(self, path: str):
        self.map.save_map(path)

    # ────────────────────────── victory and defeat ────────────────────────── #
    def victory(self, agent: Adventurer):
        """ Method to restart the simulation and handle a victory """
        self.won, self.over = True, True

    def defeat(self):
        """ Method to restart the simulation and handle defeat """
        self.won, self.over = False, True

    def kill(self, agent: Adventurer):
        """ Method handling the death of an agent """
        # @TODO: code this
        agent.kill()
        if all(map(lambda a: not a.alive, self.agents)):
            self.defeat() # every player is dead

    # ─────────────────────────── priting methods ──────────────────────────── #
    def show_last_actions(self):
        strings = []
        if any([a is None for a in self.last_actions]) or not self.last_actions:
            return 'no move yet'
        for (h, agent) in enumerate(self.agents):
            print(h, agent, self.last_actions)
            strings += ['player {} played {}'.format(
                    h, '↑→↓←'[self.last_actions[h].to_int])]
        return '\n'.join(strings)

    def colored_str(self):
        from utils import Color, color_grid
        n, m = self.n, self.m
        key = None
        sword = None
        for p in range(n * m):
            i, j = p // m, p % m
            if self.map[i, j] == Cell.golden_key:
                key = (i, j)
            if self.map[i, j] == Cell.magic_sword:
                sword = (i, j)
        color = {
                Color.blue: [sword],
                Color.red: [(0, 0), key],
                Color.green: [self.agents[0].pos]
            }
        grid = ['' for i in range(n * m)]
        for p in range(n * m):
            grid[p] = self.map[p].value
            for (h, agent) in enumerate(self.agents):
                if agent.cell_id == p:
                    if h == 0:
                        grid[p] += '*'
                    elif h == 1:
                        grid[p] = '^' + grid[p]

        colored_map = color_grid(grid, (n, m), content_colors=color)
        legends = []
        agents_symbols = '*^'
        for h, agent in enumerate(self.agents):
            legends.append('{}: agent {}\'s position'.format(agents_symbols[h], h))

        legend = '\n'.join(legends)
        return colored_map + legend + '\n'

    # ──────────────────────────── magic methods ───────────────────────────── #
    def __str__(self):
        """ adds the position of agents to the string representation """
        agents_symbols = '*^'
        assert len(self.agents) <= len(agents_symbols)
        if not self.agents:
            return str(self.map)
        map_repr = list(str(self.map))
        legends = []
        for h, agent in enumerate(self.agents):
            line = 1 + agent.i * 2
            col = 3 + agent.j * 4 - h * 2 # |^x*| when both agents are on the same cell
            map_repr[line * (self.m * 4 + 2) + col] = agents_symbols[h]
            legends.append('{}: agent {}\'s position'.format(agents_symbols[h], h))

        legend = '\n'.join(legends)
        return ''.join(map_repr) + legend # + '\n'

    def __repr__(self):
        return "Dungeon({} x {}, {} players)".format(self.n, self.m, len(self.agents))
        path_back        = astar.process_shortest_path(treasure, start)

        # ----------------------- version with colors ------------------------ #
        agents_symbols = '*^'
        assert len(self.agents) <= len(agents_symbols)
        if not self.agents:
            return str(self.map)
        legends = []
        map_str = [cell.value for cell in self.map]
        for h, agent in enumerate(self.agents):
            (i, j), s = agent.pos, agents_symbols[h]
            p = i * self.map.m + j
            map_str[p] = s + map_str[p] if h else map_str[p] + s
            legends.append('{}: agent {}\'s position'.format(s, h))

        legend = '\n'.join(legends)
        map_repr = utils.color_grid(map_str, (self.map.n, self.map.m),
                border_colors={
                    utils.Color.blue: path_to_key,
                    utils.Color.red: path_to_treasure,
                    utils.Color.green: path_back
                    })
        return map_repr + legend # + '\n'


# ──────────────────────────────── executable ──────────────────────────────── #
if __name__ == '__main__':
    np.set_printoptions(precision=5, linewidth=200)

    custom_game = Dungeon(4, 3)
    b = Cell.start
    p = Cell.magic_portal
    e = Cell.empty
    s = Cell.magic_sword
    m = Cell.moving_platform
    t = Cell.treasure
    k = Cell.golden_key

    # custom_game.map.load([t, p, p, s,
    #                       p, p, m, p,
    #                       m, p, m, m,
    #                       k, m, p, b])
    custom_game.map.load([t, e, s,
                          e, m, e,
                          e, m, e,
                          k, e, b])

    print(custom_game)

    S = custom_game.markov_chain()
    M = custom_game.moving_markov_chain()

    # print(State(0, 0, 11))

    # tr = custom_game.special_transition(S, M, State(0, 0, 11))
    # for (i, p) in enumerate(tr):
        # s = State(s_id=i)
        # if p > 0:
            # print('- {:4.2%}: {}'.format(p, s))

    T = custom_game.make_transition_matrix()
    custom_game.display_transition(State(0, 0, 15), Direction.NORTH)
