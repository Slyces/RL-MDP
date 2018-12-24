# ───────────────────────────────── imports ────────────────────────────────── #
from kernel import Dungeon, Direction
from time import sleep
import os, sys
# ──────────────────────────────────────────────────────────────────────────── #

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


# ────────────────────────────── text interface ────────────────────────────── #
class TextInterface(object):
    """ Text Interface to play interactively the MDP game """
    def __init__(self, dungeon: Dungeon):
        self.dungeon = dungeon
        assert len(dungeon.agents) == 1, "currently designed for 1 adventurer"
        self.player, = dungeon.agents

    # ─────────────────── display the state of the dungeon ─────────────────── #
    def display(self):
        os.system('clear')
        print(self.dungeon)
        print(self.infos)
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
        """ waits for input from the player """
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
