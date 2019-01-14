This code is provided with a main.py executable. It contains a command line interface to execute every different part of our code, using the options.
We did work on the -h to make it as explicit as we could, so do not hesitate to read it.

run the code with python, or make the main.py file executable

python3 main.py -h

-------------------------------------------------------
We have two interfaces :
    - text, only working on linux
    - graphical, crossplatform
Both require a specific font to be added to your system.
It is the easier way to make our code work. Without the
font, the text version will work but you will probably
have issues with unknown symbols and not evenly sized
characters if your font is not monospaced.

See the report.pdf to find the instructions to add the
font. You can use a letters only display by changing
dungeon_game/dungeon_map.py, line 27, pretty_cells = True
to pretty_cells = False.
-------------------------------------------------------

To play the game interactively, use

python3 main (-t) -gi

where (-t) is to use text, graphical is default.
-------------------------------------------------------

To use a random map, use -g. To load a map, use -l.

To watch a policy, use -p [agent-name].

The policy moves automatically, to force a keypress
between moves, use --step-by-step.

Others options can be found in the -h.
