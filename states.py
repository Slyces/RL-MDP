# ───────────────────────────────── imports ────────────────────────────────── #
pass
# ──────────────────────────────────────────────────────────────────────────── #

class State(object):
    """ State of the MDP as designed in the dungeon """

    # ────────────────────────── static attributes ─────────────────────────── #
    n, m, max_id = 0, 0, 0
    swords = 2
    treasures = 3

    def configure(n: int, m: int):
        """ Configures the static parameters of the class """
        State.n, State.m = n, m
        State.max_id = n * m * State.swords * State.treasures # account for death

    # ───────────────────────────── constructor ────────────────────────────── #
    def __init__(self, sword: int = None, treasure: int = None, position: int = None,
                 s_id: int = None):
        """
        Creates a state object. Two way to initialze:
            - Using the 3 separate values composing a state:

                State(sword=0, treasure=1, position=4) <=> State(0, 1, 4)

            - Using the state id:

                State(s_id=14) # must use the keyword
        """
        assert (sword is not None and treasure is not None and position is not None) or \
               s_id is not None
        self.__sword, self.__treasure, self.__position, self.__id = -1, -1, -1, -1
        if s_id is not None:
            self.id = s_id
            # self.sword, self.treasure, self.position = State.id_to_state(s_id)
        else:
            # self.sword, self.treasure, self.position = sword, treasure, position
            self.id = State.state_to_id(sword, treasure, position)

    # ─────────────────── use getters for the same reason ──────────────────── #
    @property
    def sword(self): return self.__sword

    @property
    def treasure(self): return self.__treasure

    @property
    def position(self): return self.__position

    @property
    def id(self): return self.__id

    # ──────────────── use setters to garanty value coherency ──────────────── #
    @sword.setter
    def sword(self, value: int):
        self.__sword = value
        self.__id = State.state_to_id(self.sword, self.treasure, self.position)

    @treasure.setter
    def treasure(self, value: int):
        self.__treasure = value
        self.__id = State.state_to_id(self.sword, self.treasure, self.position)

    @position.setter
    def position(self, value: int):
        self.__position = value
        self.__id = State.state_to_id(self.sword, self.treasure, self.position)

    @id.setter
    def id(self, value: int):
        self.__id = value
        self.__sword, self.treasure, self.position = State.id_to_state(value)

    # ──────────────── static conversions : state <--> values ──────────────── #
    @staticmethod
    def id_to_state(s_id: int):
        position = s_id % (State.n * State.m)
        treasure = (s_id // (State.n * State.m)) % State.treasures
        sword = (s_id // (State.n * State.m * State.treasures)) % State.swords
        return sword, treasure, position

    @staticmethod
    def state_to_id(sword: int, treasure: int, position: int):
        n, m = State.n, State.m
        return sword * State.treasures * n * m + treasure * n * m + position

    # ───────────────────────── some usefull getters ───────────────────────── #
    @property
    def i(self):
        return self.position // State.m

    @property
    def j(self):
        return self.position % State.m

    @i.setter
    def i(self, v: int):
        self.position = v * State.m + self.j

    @j.setter
    def j(self, v: int):
        self.position = self.i + v

    def __str__(self):
        sw = '理'
        tr = 'ﰤ'
        return "<S: {} ,T: {} ,p: ({},{})>".format(sw[self.sword], tr[self.treasure], self.i, self.j)


