# ───────────────────────────────── imports ────────────────────────────────── #
from random import random
from characters import Adventurer
from dungeon_map import DungeonMap, Direction, Cell, AStar
import utils
# ──────────────────────────────────────────────────────────────────────────── #
# @TODO (for the indian coding team) visualize a policy

# ────────────── Kernel classes for the MADI project (01/2019) ─────────────── #
class Dungeon(object):
    """ Dungeon object containing all the game logic """

    p_enemy = 0.7

    def __init__(self, n: int, m: int, nb_players: int = 1):
        self.n, self.m = n, m
        self.map = DungeonMap(n, m)
        while not self.winnable:
            self.map = DungeonMap(n, m)
        self.agents = [Adventurer(n - 1, m - 1, n, m) for i in range(nb_players)]
        self.over = False
        self.caption = ''

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
        # ------------------ treasure is particular, though ------------------ #
        elif cell == Cell.treasure and agent.has_item(Cell.golden_key):
            self.caption += "Got the treasure !"
            agent.acquire_item(cell)
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
        elif cell == Cell.enemy and not agent.has_item(Cell.magic_sword):
            # no fight for the brave wielding a sword
            self.caption += "Enemy in sight ! "
            p = random() # random floating number in [0, 1[
            if p < Dungeon.p_enemy: # the player is victorious (p_enemy)%
                self.caption += "Easily defeated."
            else:
                self.caption += "Woops, I'm dead"
                self.kill(agent)
        elif cell == Cell.enemy:
            self.caption += "BIM ! BAM ! MAGIC SWORD IN YOUR FACE !"
        # ------------ returning to the start (with the treasure) ------------ #
        elif cell == Cell.start and agent.has_item(Cell.treasure):
            self.caption += "I WON. !!!"
            self.victory(agent)
            return 1

        # ───────────── handle the reward in various situations ────────────── #
        return -1 if not agent.alive else 0

    # ────────────────────────── victory and defeat ────────────────────────── #
    def victory(self, agent: Adventurer):
        """ Method to restart the simulation and handle a victory """
        self.over = True

    def defeat(self):
        """ Method to restart the simulation and handle defeat """
        self.over = True

    def kill(self, agent: Adventurer):
        """ Method handling the death of an agent """
        # @TODO: code this
        agent.kill()
        if all(map(lambda a: not a.alive, self.agents)):
            self.defeat() # every player is dead

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
        return ''.join(map_repr) + legend + '\n'

    def __repr__(self):
        return "Dungeon({} x {}, {} players)".format(self.n, self.m, len(self.agents))

    # ─────────────────── print the different astar paths ──────────────────── #
    def display_paths(self):
        # --------------------- find the different paths --------------------- #
        astar = AStar(unreachable=(Cell.wall, Cell.crack, Cell.magic_portal))
        astar.load_map(self.map)
        key, treasure, start = None, (0, 0), (self.n - 1, self.m - 1)
        for h in range(self.m * self.n):
            if self.map[h] == Cell.golden_key:
                key = (h // self.m, h % self.m)
        path_to_key      = astar.process_shortest_path(start, key)
        path_to_treasure = astar.process_shortest_path(key, treasure)
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
        return map_repr + legend + '\n'

# ──────────────────────────────── executable ──────────────────────────────── #
if __name__ == '__main__':
    d = Dungeon(8, 8)
    print(d)
