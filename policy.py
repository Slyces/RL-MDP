# ───────────────────────────────── imports ────────────────────────────────── #
from kernel import Dungeon
from characters import Adventurer
# ──────────────────────────────────────────────────────────────────────────── #
# This file is an interface for a policy object, describing every primitives
# needed to display a policy in action

# Every decision algorithm should implement this interface (MDP, RL, Deep-RL?)

# ───────────────────────────── Policy interface ───────────────────────────── #
class Policy(object):
    """
    Interface for a policy object allowing automatic decision for an agent in
    a given dungeon
    """
    def __init__(self, dungeon: Dungeon, agent: Adventurer):
        """ Every policy takes place in a dungeon for a particular agent """
        assert agent in dungeon.agents
        self.dungeon = dungeon
        self.agent = agent

    # ─────────────── core of the policy : get the next action ─────────────── #
    def next_action(self):
        """
        Implicit input: the actual state of the agent, and the actual state
        of the dungeon

        @return a Direction (it's the only available actions)
        """
        pass # Not implemented
