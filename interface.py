# encoding: utf-8
# ───────────────────────────────── imports ────────────────────────────────── #
from game.kernel import Dungeon, Direction
from game.dungeon_map import Cell
from game.utils import add_sword
from time import sleep
from tkinter.font import Font
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
    def play_game(self, time_step: int= 500):
        time_step /= 1000
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
        return [add_sword(x.center(3, ' '), True).strip() for x in L]

    # ─────────────────── display the state of the dungeon ─────────────────── #
    def display(self):
        os.system('clear')
        # print(self.dungeon)
        print(add_sword(self.dungeon.colored_str(), Cell.pretty_cells))
        print('-' * (1 + self.dungeon.m * 4))
        print(self.dungeon.show_last_actions())
        print('-' * (1 + self.dungeon.m * 4))
        print(add_sword(self.infos, Cell.pretty_cells))
        print('-' * (1 + self.dungeon.m * 4))
        print(self.dungeon.caption)
        self.dungeon.caption = ''

    @property
    def infos(self):
        # inf = ['-' * (1 + self.dungeon.m * 4)]
        inf = []
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
        if ch in ('\x03',):
            sys.exit(1)

# ─────────────────────── class for the qlearning logs ─────────────────────── #
class LearningInterface(TextInterface):
    def display(self):
        # os.system('clear')
        # print(self.dungeon) # no color
        print(add_sword(self.dungeon.colored_str(), Cell.pretty_cells)) # color
        print('-' * (1 + self.dungeon.m * 4))
        print(self.dungeon.show_last_actions())
        print('-' * (1 + self.dungeon.m * 4))
        print(add_sword(self.infos, Cell.pretty_cells))
        print('-' * (1 + self.dungeon.m * 4))
        print(self.dungeon.caption)
        self.dungeon.caption = ''

# ─────────────────────────── graphical interface ──────────────────────────── #
class GraphicalInterface(TextInterface, tk.Tk):
    """ Tkinter implementation of a Dungeon GUI """
    def __init__(self, dungeon: Dungeon, *args, **kwargs):
        TextInterface.__init__(self, dungeon)
        tk.Tk.__init__(self, *args, **kwargs)
        self.title = "WELCOME TO THE DUNGEON"
        self.bind('<Key>', self.on_keypress)

        n, m = dungeon.n, dungeon.m

        myFont = Font(family="RobotoMono Nerd Font", size=12, weight='normal')
        myInfoFont = Font(family="RobotoMono Nerd Font", size=10, weight='normal')

        cell_size = 40 

        self.fg = fg = '#F2F3F4'
        bg = '#3B444B'
        active_fg = '#0095B6'
        active_bg = '#1B242B'

        # ───────────────────────── create the grid ────────────────────────── #
        self.board = tk.Frame(self)
        self.board.pack(padx=1, pady=1)
        self.frames = [None for x in range(n * m)]
        self.cells = [None for x in range(n * m)]
        for x in range(n * m):
            r, c = x // m, x % m

            # ----------- create frames for a fixed size in pixels ----------- #
            self.frames[x] = tk.Frame(self.board, height=cell_size, width=cell_size,
                    bg=bg)
            self.frames[x].pack_propagate(False)
            self.frames[x].grid(row=r, column=c, padx=1, pady=1)

            # ----------- create the labels to display game state ------------ #
            self.cells[x] = tk.Label(self.frames[x], bg=bg, fg=fg, font=myFont,
                    activeforeground= active_fg, activebackground=active_bg)
            self.cells[x].pack(expand=True, fill='both')

        # ────────────────────────── infos display ─────────────────────────── #
        f_width = myInfoFont.measure('x')
        w = max(50, int((cell_size * m) / f_width))

        # force_width = tk.Frame(self, width=max(450, cell_size * m))
        # force_width.pack_propagate(False)
        # force_width.pack()

        frame = tk.Frame(self)
        frame.pack()

        self.message_actions = tk.Label(frame, font=myInfoFont, width=w, justify='left')
        self.message_actions.pack(expand=True, fill='x')

        self.message_infos = tk.Label(frame, font=myInfoFont, width=w, justify='left')
        self.message_infos.pack(expand=True, fill='x')

        self.message_caption = tk.Label(frame, font=myInfoFont, width=w, justify='left')
        self.message_caption.pack(expand=True, fill='x')

        # ──────────────────────── display everything ──────────────────────── #
        self.display()

    # ──────────────────── refresh display with new state ──────────────────── #
    def display(self):
        dungeon_cells = self.list_display()
        for (i, label) in enumerate(self.cells):
            cell = self.dungeon.map[i]
            label.configure(text=dungeon_cells[i], fg=self.fg,
                    state='active' if i == self.player.cell_id else 'normal')
            if cell in (Cell.magic_sword, Cell.magic_rune, Cell.magic_book):
                label.configure(fg='#8FBC8F')
            if cell in (Cell.golden_key, Cell.treasure):
                label.configure(fg='#B31B1B')
        # --------------------------- adding infos --------------------------- #
        # text_info = '-' * (1 + self.dungeon.m * 4) + '\n'
        actions     = self.dungeon.show_last_actions()
        infos       = add_sword(self.infos, Cell.pretty_cells)
        # caption     = '-' * (1 + self.dungeon.m * 4) + '\n' + self.dungeon.caption
        caption     = self.dungeon.caption

        self.message_actions.configure(text=actions)
        self.message_infos.configure(text=infos)
        self.message_caption.configure(text=caption)

        # ------------------------- reseting caption ------------------------- #
        self.dungeon.caption = ''

    # ────────────────────────── handling keypress ─────────────────────────── #
    def on_keypress(self, event):
        if not self.dungeon.over:
            self.handle_input(event.char)
            self.display()
        if self.dungeon.over and \
                'GAME' not in self.message_caption['text'].split('\n')[-1]:
            print(' GAME OVER '.center(35, '-'))
            self.message_caption['text'] += '\n' + ' GAME OVER '.center(35, '-')

    # ──────────────── automatic agent∙s playing on keypress ───────────────── #
    def play_game_step(self):
        """ Show an agent playing the game step by step """
        self.dungeon.reset()
        players = self.dungeon.agents
        self.display()
        self.bind('<Key>', lambda ev: self.next_step(ev, players))
        self.loop()

    def next_step(self, ev, players):
        if not ev.char:
            return
        if self.dungeon.over and \
                'GAME' not in self.message_caption['text'].split('\n')[-1]:
            print(' GAME OVER '.center(35, '-'))
            self.message_caption['text'] += '\n' + ' GAME OVER '.center(35, '-')
        elif not self.dungeon.over:
            actions = [agent.play(agent.state) for agent in players]
            for (action, player) in zip(actions, players):
                self.dungeon.move(player, action)
        self.display()

    # ────────────────────── automatic agent∙s playing ─────────────────────── #
    def play_game(self, time_step: int= 500):
        """ Shows an agent playing the game """
        self.dungeon.reset()
        players = self.dungeon.agents
        self.display()
        self.after(time_step, lambda : self.next_actions(players, time_step))
        self.loop()

    def next_actions(self, players, time_step):
        if self.dungeon.over and \
                'GAME' not in self.message_caption['text'].split('\n')[-1]:
            print(' GAME OVER '.center(40, '-'))
            self.message_caption['text'] += '\n' + ' GAME OVER '.center(40, '-')
        elif not self.dungeon.over:
            actions = [agent.play(agent.state) for agent in players]
            for (action, player) in zip(actions, players):
                self.dungeon.move(player, action)
            self.after(time_step, lambda : self.next_actions(players, time_step))
        self.display()

    # ────────────────────────────── main loop ─────────────────────────────── #
    def loop(self):
        self.mainloop()

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


