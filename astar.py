
# ────────────────────────── A Star implementation ─────────────────────────── #
class AStar(object):
    """ Special AStar algorithm adapted to this specific labyrinth """

    dist = DungeonMap.distance  # we reuse the Manhattan distance

    def __init__(self, unreachable: list = (Cell.wall, Cell.crack)):
        """
        Creates an instance of the AStar algorithm
            - unreachable: list of cells forbidden (not accessible)
        """
        self.unreachable = unreachable
        self.objective = (-1, -1)
        self.map, self.grid = None, None

    # ─────────────── loads a map for the next shortest paths ──────────────── #
    def load_map(self, d_map):
        """
        Loads a dungeon map that will be used for every pathfinding

        @return None
        """
        self.map = d_map
        n, m = d_map.n, d_map.m
        self.grid = [{'parent': None, 'f': 0, 'g': 0, 'h': 0} for h in range(n * m)]

    def unload_map(self):
        """
        Unloads a dungeon map

        @return None
        """
        self.map, self.grid = None, None

    # ────────────── method to check if the algorithm is ready ─────────────── #
    @property
    def ready(self):
        """
        The algorithm needs to be configured before finding a shortest path

        @return bool: True if ready to find a shortest path
        """
        return self.objective != (-1, -1) and self.grid is not None and self.map is not None

    # ──────────────────── test if a cell can be reached ───────────────────── #
    def reachable(self, pos: (int, int)):
        """
        returns a boolean if the pos is accessible

        @param pos: position of a cell
        @return bool: is that cell accessible ?
        """
        return self.map is not None and self.map[pos] not in self.unreachable

    def heuristic(self, pos: (int, int)):
        """
        Computes the heuristic value H for a cell: distance betweenthis cell
        and the objective cell, multiplied by 10

        @param pos: tuple of 2 ints (coordinates)
        @returns heuristic value H
        """
        assert self.ready
        return 10 * self.dist(pos, self.objective)

    # ──────────────────────────── display a path ──────────────────────────── #
    def get_path(self):
        """ Returns the last path found by the AStar object """
        path = [self.objective]
        while self[path[-1]]['parent'] != self.start:
            path += [self[path[-1]]['parent']]
        return path + [self.start]

    def display_path(self, path: list = None):
        """ Shows the path found by the algorithm """
        path = self.get_path() if path is None else path
        print('path : ' + ' → '.join([str(x) for x in path[::-1]]))

    # ──────────────────────────── adjacent cells ──────────────────────────── #
    def adjacent_cells(self, pos: (int, int)):
        """
        Returns a generator of the positions adjacent to the given position
        Counter-clockwise, starting from the top and finishing to the right

        @param pos: a valid position (coordinates) in the map
        @return generator of the neighboring positions of 'pos'
        """
        i, j = pos
        assert 0 <= i < self.map.n and 0 <= j < self.map.m
        if i < self.map.n - 1: yield (i + 1, j)
        if 0 < i: yield (i - 1, j)
        if j < self.map.m - 1: yield (i, j + 1)
        if 0 < j: yield (i, j - 1)

    # ──────────────────────────── update a cell ───────────────────────────── #
    def update_cell(self, adj, cell):
        """
        Update adjacent cell

        @param adj adjacent cell to the current cell
        @param cell current cell being processed
        """
        self[adj]['g'] = self[cell]['g'] + 10
        self[adj]['h'] = self.heuristic(adj)
        self[adj]['f'] = self[adj]['h'] + self[adj]['g']
        self[adj]['parent'] = cell

    # ─────────── main part of the algorithm : find shortest path ──────────── #
    def process_shortest_path(self, start, objective):
        self.start, self.objective = start, objective
        # add starting cell to open heap queue
        opened, closed = [], []
        opened.append((self[start]['f'], start))
        while len(opened):
            # pop cell from heap queue
            f, cell = opened.pop(0)
            # add cell to closed list so we don't process it twice
            closed.append(cell)
            # if ending cell, display found path
            if cell == objective:
                return self.get_path()
            # get adjacent cells for cell
            for adj_cell in self.adjacent_cells(cell):
                if self.reachable(adj_cell) and adj_cell not in closed:
                    if (self[adj_cell]['f'], adj_cell) in opened:
                        # if adj cell in open list, check if current path is
                        # better than the one previously found for this adj
                        # cell.
                        if self[adj_cell]['g'] > self[cell]['g'] + 10:
                            self.update_cell(adj_cell, cell)
                    else:
                        self.update_cell(adj_cell, cell)
                        # add adj cell to open list
                        opened.append((self[adj_cell]['f'], adj_cell))

    # ──────────────────────────── magic methods ───────────────────────────── #
    def __getitem__(self, index):
        """
        Easier way to access the cells of the currently loaded map
        ex:
            self[4, 7] instead of self.map[4, 7]

        @return Cell: the cell present at (index), or an IndexError
        """
        return self.grid[index] if isinstance(index, int) else self.grid[index[0] * self.map.m + index[1]]
