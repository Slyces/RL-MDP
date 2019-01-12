# encoding: utf-8
# ───────────────────────────────── imports ────────────────────────────────── #
from kernel import Dungeon, Direction
from dungeon_map import Cell
from time import sleep
from utils import add_sword
import os, sys, tkinter as tk
# ──────────────────────────────────────────────────────────────────────────── #

# ────────────────────────────── text interface ────────────────────────────── #
class TextInterface(object):
    """ Text Interface to play interactively the MDP game """
    def __init__(self, dungeon: Dungeon):
        self.dungeon = dungeon
        assert len(dungeon.agents) == 1, "currently designed for 1 adventurer"
        self.player, = dungeon.agents

    # ──────────────────── play a game with an Adventurer ──────────────────── #
    def play_game(self, time_step: float= 0.5):
        self.dungeon.reset()
        players = self.dungeon.agents
        self.display()
        sleep(time_step)
        while not self.dungeon.over:
            actions = [agent.play(agent.state) for agent in players]
            for (action, player) in zip(actions, players):
                self.dungeon.move(player, action)
            self.display()
            sleep(time_step)

    # ──────────────────── play a game with an Adventurer ──────────────────── #
    def play_game_step(self):
        self.dungeon.reset()
        players = self.dungeon.agents
        self.display()
        while not self.dungeon.over:
            getch()
            actions = [agent.play(agent.state) for agent in players]
            for (action, player) in zip(actions, players):
                self.dungeon.move(player, action)
            self.display()

    # ───────────────── list display : list of cells content ───────────────── #
    def list_display(self):
        L = [cell.value for cell in self.dungeon.map]
        L[self.player.cell_id] += '*'
        return [add_sword(x, Cell.pretty_cells) for x in L]

    # ─────────────────── display the state of the dungeon ─────────────────── #
    def display(self):
        os.system('clear')
        # print(self.dungeon)
        print(add_sword(self.dungeon.colored_str(), Cell.pretty_cells))
        print('-' * (1 + self.dungeon.m * 4))
        print(self.dungeon.show_last_actions())
        print(add_sword(self.infos, Cell.pretty_cells))
        print(self.dungeon.caption)
        self.dungeon.caption = ''

    @property
    def infos(self):
        inf = ['-' * (1 + self.dungeon.m * 4)]
        for agent in self.dungeon.agents:
            inf += [agent.infos]
        return '\n'.join(inf)

    # ────────────────────────────── main loop ─────────────────────────────── #
    def loop(self):
        """ Main loop of interaction with the human player """
        self.display()
        while not self.dungeon.over:
            self.handle_input(getch()) # get the next char input by user
            self.display()
        print(' GAME OVER '.center(80, '-'))

    def handle_input(self, ch: str):
        """ handles input from player """
        if ch in ('l', 'd'): # →
            self.dungeon.move(self.player, Direction.EAST)
        if ch in ('j', 's'): # ↓
            self.dungeon.move(self.player, Direction.SOUTH)
        if ch in ('h', 'q'): # ←
            self.dungeon.move(self.player, Direction.WEST)
        if ch in ('k', 'z'): # ↑
            self.dungeon.move(self.player, Direction.NORTH)
        if ch in ('\x03'):
            sys.exit(1)

# ─────────────────────── class for the qlearning logs ─────────────────────── #
class LearningInterface(TextInterface):
    def display(self):
        # os.system('clear')
        # print(self.dungeon) # no color
        print(add_sword(self.dungeon.colored_str(), Cell.pretty_cells)) # color
        print('-' * (1 + self.dungeon.m * 4))
        print(self.dungeon.show_last_actions())
        print(add_sword(self.infos, Cell.pretty_cells))
        print(self.dungeon.caption)
        self.dungeon.caption = ''

# ─────────────────────────── graphical interface ──────────────────────────── #
class GraphicalInterface(TextInterface, tk.Tk):
    """ Tkinter implementation of a Dungeon GUI """
    def __init__(self, dungeon: Dungeon, *args, **kwargs):
        TextInterface.__init__(self, dungeon)
        tk.Tk.__init__(self, *args, **kwargs)
        self.title = "WELCOME TO THE DUNGEON"

        n, m = dungeon.n, dungeon.m

        cell_size = 40 

        fg = ''
        active_fg = '#F2F3F4'
        active_bg = 'black'

        dungeon_cells = self.list_display()

        # ───────────────────────── create the grid ────────────────────────── #
        self.board = tk.Frame(self)
        self.board.pack(padx=1, pady=1)
        self.frames = [None for x in range(n * m)]
        self.cells = [None for x in range(n * m)]
        for x in range(n * m):
            r, c = x // m, x % m
            self.frames[x] = tk.Frame(self.board, height=cell_size, width=cell_size,
                    bg='#3B444B').grid(row=r, column=c, padx=1, pady=1) 
            self.cells[x] = tk.Label(self.frames[x], text= dungeon_cells[x],
                    activeforeground= active_fg, activebackground=active_bg,
                    bg='')

    def loop(self):
        self.mainloop()

    def play_game(self, time_step: float= 0.5):
        """ Shows an agent playing the game """
        # @TODO
        pass

# ───────────────────── getchar code from stackoverflow ────────────────────── #
def _find_getch():
    try:
        import termios
    except ImportError:
        # Non-POSIX. Return msvcrt's (Windows') getch.
        import msvcrt
        return msvcrt.getch

    # POSIX system. Create and return a getch that manipulates the tty.
    import sys, tty
    def _getch():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

    return _getch

getch = _find_getch()


