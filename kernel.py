# ───────────────────────────────── imports ────────────────────────────────── #
from random import random
from characters import Adventurer
from dungeon_map import DungeonMap, Direction, Cell
# ──────────────────────────────────────────────────────────────────────────── #

# ────────────── Kernel classes for the MADI project (01/2019) ─────────────── #
class Dungeon(object):
    """ Dungeon object containing all the game logic """

    p_enemy = 0.7

    def __init__(self, n: int, m: int, nb_players: int = 1):
        self.n, self.m = n, m
        self.map = DungeonMap(n, m)
        self.agents = [Adventurer(n - 1, m - 1) for i in range(nb_players)]
        self.over = False

    # ──────────────────────────── moving agents ───────────────────────────── #
    def move(self, agent: Adventurer, direction: Direction):
        """ Moves an agent in a direction """
        agent.pos = self.map.move(agent.pos, direction)
        self.enter(agent, self.map[agent.pos])

    def teleport(self, agent: Adventurer, position: (int, int)):
        """ Teleports an agent to a given position (might be usefull for animations)"""
        i, j = position
        assert 0 <= i < self.n and 0 <= j < self.m, "can't teleport outside of the dungeon"
        assert self.map[position] != Cell.wall, "can't teleport in a wall"
        agent.position = position

    # ─────────────────────────── entering a cell ──────────────────────────── #
    def enter(self, agent: Adventurer, cell: Cell):
        """
        Performs the most simple cells tasks, and delegates to appropriate
        functions if needed
        """
        assert cell != Cell.wall, "wall cells should never be entered"
        p = random() # random floating number in [0, 1[
        # ---------------- items are treated in the same way ----------------- #
        if cell == Cell.golden_key or cell == Cell.magic_sword:
            agent.acquire_item(cell)
        # ------------------ treasure is particular, though ------------------ #
        elif cell == Cell.treasure and agent.has_item(Cell.golden_key):
            agent.acquire_item(cell)
        # ------------ magic portal and moving platforms teleport ------------ #
        elif cell == Cell.magic_portal:
            self.teleport(agent, self.map.random_cell())
        elif cell == Cell.moving_platform:
            self.teleport(agent.position, 1) # adjacent cell <=> Manhattan dist of 1
        # ---------------------- oh, CRACK, you're dead ---------------------- #
        elif cell == Cell.crack:
            self.kill(agent)
        # ----------------------- care, it's a trap !! ----------------------- #
        elif cell == Cell.trap:
            if p < 0.1:
                self.kill(agent) # 10% : death
            if p < 0.4:
                self.teleport(agent, (self.n - 1, self.m - 1)) # 30% : back to start
            # 60% : nothing
        # ----------------------------- FIGHT !! ----------------------------- #
        elif cell == Cell.enemy and not agent.has_item(Cell.magic_sword):
            # no fight for the brave wielding a sword
            if p >= Dungeon.p_enemy: # the player is defeated (1 - p_enemy)%
                self.kill(agent)
        elif cell == Cell.start and agent.has_item(Cell.golden_key):
            self.victory(agent)

    # ────────────────────────── victory and defeat ────────────────────────── #
    def victory(self, agent: Adventurer):
        """ Method to restart the simulation and handle a victory """
        # @TODO: code this
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

# ──────────────────────────────── executable ──────────────────────────────── #
if __name__ == '__main__':
    d = Dungeon(8, 8)
    print(d)
