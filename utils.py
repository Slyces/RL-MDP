# ───────────────────────────────── imports ────────────────────────────────── #
from enum import Enum
# ──────────────────────────────────────────────────────────────────────────── #
verbose = 0
def vprint(*args, v=1, **kwargs):
    """ prints its content if verbose >= v """
    if verbose >= v: print(*args, **kwargs)

# ──────────────────────────────────────────────────────────────────────────── #
class Color(Enum):
    black      = 30
    red        = 31
    dark_green = 32
    yellow     = 33
    blue       = 34
    purple     = 35
    green      = 36
    white      = 37


def add_color(string: str, fg: Color= Color.white):
    """
    Colors a string using escape characters
        (works in linux terms, untested for windows)
    """
    c = "\x1b[{};{};{}m".format(0, fg.value, 40) # color escape code
    e = "\x1b[0m" # endline
    return c + string + e

def color_grid(array, size:int, cell_size: int=3, border_colors: dict= None,
        content_colors: dict= None):
    """
    Arranges a two dimensional array (stored in a 1D list) into a grid.
    ex:                ┌───┬───┐
        [[T, K],       │ T │ K │
         [S, ◉]]  ⟶    ├───┼───┤
                       │ S │ ◉ │
                       └───┴───┘
    @param array: the array to be converted
    @param size: the dimensions of the array
    @param cell_size: length (in characters) of every cell of the output
    @param border_colors: dict(color -> list of cells) indicating cells
                          to color (only the borders) in the string
    @param content_colors: dict(color -> list of cells) indicating cells
                           to color (only the content) in the string

    @return str: the string representation of the final grid
    """
    n, m = size

    connectors = [['┌'] + ['┬'] * (m - 1) + ['┐']] + \
                 [['├'] + ['┼'] * (m - 1) + ['┤']] * (n - 1) + \
                 [['└'] + ['┴'] * (m - 1) + ['┘']]
    top_border = '─' * cell_size
    side_border = '│'

    to_color = [[{'content': None, 'border': None} for i in range(m)] for j in range(n)]
    for color_type in ('content', 'border'):
        color_dict = locals()[color_type + '_colors']
        if color_dict is not None:
            for (color, cells_list) in color_dict.items():
                for cell in cells_list:
                    a, b = cell
                    to_color[a][b][color_type] = color

    # ---------- find a color for the cell, clockwise (↑, →, ↓, ←) ----------- #
    def cell_color(row, col, ctype):
        #ctypes : row, col, both
        if ctype in ('row', 'both') and row > 0 and col < m and to_color[row - 1][col]['border']:
            # return top (↑) color if available
            # +---+---+---+ < row = 0
            # | . | . | . | < array.row = 0
            # +---+---+---+ < row = 1 <-- value received
            # | . | . | . | < array.row = 1 : color returned
            # +---+---+---+ < row = 2
            return to_color[row - 1][col]['border']
        if ctype in ('col', 'both') and row < n and col < m and to_color[row][col]['border']:
            # return right (→) color if available
            # 0   1   2   3 conn  cols [received]
            # v 0 v 1 v 2 v array cols 
            # +---+---+---+
            # | . | . | . |
            # +---+---+---+
            # | . | . | . |
            # +---+---+---+
            return to_color[row][col]['border']
        if ctype in ('row', 'both') and row < n and col < m and to_color[row][col]['border']:
            # return bot (↓) color if available
            # +---+---+---+ < row = 0
            # | . | . | . | < array.row = 0 : color returned
            # +---+---+---+ < row = 1 <-- value received
            # | . | . | . | < array.row = 1
            # +---+---+---+ < row = 2
            return to_color[row][col]['border']
        if ctype in ('col', 'both') and col > 0 and row < n and to_color[row][col - 1]['border']:
            # return left (←) color if available
            # 0   1   2   3 conn  cols [received]
            # v 0 v 1 v 2 v array cols 
            # +---+---+---+
            # | . | . | . |
            # +---+---+---+
            # | . | . | . |
            # +---+---+---+
            return to_color[row][col - 1]['border']
        return None

    all_cells = [['' for i in range(2 * m + 1)] for j in range(2 * n + 1)]
    for i in range(n):
        for j in range(m):
            # -------------------- processing cell (i, j) -------------------- #
            #     j j j+1   2j 2j+1 2(j+1)
            # i   +---+     +  ---  +     2 * i
            # i   | a |     |   a   |     2 * i + 1
            # i+1 +---+     +  ---  +     2 * (i + 1)
            # Here, only doing :
            #     +---
            #     | a

            # top left
            color = cell_color(i, j, 'both')
            top_left = connectors[i][j]
            all_cells[2*i][2*j] = top_left if color is None else add_color(top_left, color)

            # top
            color = cell_color(i, j, 'row')
            all_cells[2*i][2*j+1] = top_border if color is None else add_color(top_border, color)

            # left side
            color = cell_color(i, j, 'col')
            all_cells[2*i+1][2*j] = side_border if color is None else add_color(side_border, color)

            # content
            color = to_color[i][j]['content']
            content = array[i * m + j].center(cell_size, ' ')
            all_cells[2*i+1][2*j+1] = content if color is None else add_color(content, color)

            # --------------- doing the right if last column ----------------- #
            if j == m - 1:
                # right side
                color = cell_color(i, j + 1, 'col')
                all_cells[2*i+1][2*(j+1)] = side_border if color is None else add_color(side_border, color)

                # top right
                color = cell_color(i, j + 1, 'both')
                top_left = connectors[i][j + 1]
                all_cells[2*i][2*(j+1)] = top_left if color is None else add_color(top_left, color)

            # ------------------- doing bottom if last row ------------------- #
            if i == n - 1:
                # bottom left
                color = cell_color(i + 1, j, 'both')
                top_left = connectors[i + 1][j]
                all_cells[2*(i+1)][2*j] = top_left if color is None else add_color(top_left, color)

                # bottom
                color = cell_color(i + 1, j, 'row')
                all_cells[2*(i+1)][2*j+1] = top_border if color is None else add_color(top_border, color)

            # --------- doing bottom right if last row & last column --------- #
            if i == n - 1 and j == m - 1:
                # bottom right
                color = cell_color(i + 1, j + 1, 'both')
                top_left = connectors[i + 1][j + 1]
                all_cells[2*(i+1)][2*(j+1)] = top_left if color is None else add_color(top_left, color)

    return '\n'.join([''.join(line) for line in all_cells]) + '\n'
