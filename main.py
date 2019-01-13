#!/usr/bin/env python3
# encoding: utf-8
# ───────────────────────────────── imports ────────────────────────────────── #
from interface import TextInterface, GraphicalInterface
from dungeon_game.characters import *
from dungeon_game.mdp import *
from dungeon_game.kernel import Dungeon
import argparse, textwrap
# ──────────────────────────────────────────────────────────────────────────── #

def setup_parser():
    # ------------------------- program description -------------------------- #
    default = "[default: %(default)s]"
    parser = argparse.ArgumentParser(prog='main',
            formatter_class=argparse.RawTextHelpFormatter,
            description=textwrap.dedent('''\
                Markovian Decision Process and Reinforcement Learning
                -----------------------------------------------------
                    This program implements a game environment (a dungeon) 
                    and some artificial agents that play in that environment.
                
                    With this program, you can:
                    - use a text or graphical interface
                    - play interactively the game
                    - watch an agent play the game step by step
                        - MDP policy computed using the value iteration
                          algorithm
                        - MDP policy computed using the policy iteration
                          algorithm
                    - load a map from a txt (using our special format)
                    - save a map to a txt
                    - generate a random map

                Example of uses
                ---------------
                main -tgi : play interactively a generated map in text mode
                main -p value-mdp -g --automatic : watch the optimal policy
                                                   in graphical mode
                '''))

    game_modes = parser.add_mutually_exclusive_group()
    maps = parser.add_mutually_exclusive_group()
    timestep = parser.add_argument_group()

    # ------------------------- optionnal parameters ------------------------- #
    # Load a map from file
    maps.add_argument('-l', "--load-map", metavar="map-path", dest='map_path',
            type=str, default='', help=textwrap.dedent("""\
            load a map from a txt. provide the complete or relative path
            """))

    # Save random map to file
    parser.add_argument('-s', "--save-map", metavar="save-path", dest='save_path',
            type=str, default='', help=textwrap.dedent("""\
            save the played map to a txt. provide the complete or relative path
            only usefull if you generate a random map
            """))

    # Number of rows
    parser.add_argument("-r", "--rows", metavar="r", dest='r', type=int, default=4,
    help=textwrap.dedent("""\
            number of rows of the dungeon
            """) + default)

    # Number of cols
    parser.add_argument("-c", "--cols", metavar="c", dest='c', type=int, default=4,
    help=textwrap.dedent("""\
            number of columns of the dungeon
            """) + default)

    # Value of the step between two actions (in ms)
    timestep.add_argument("--step-value", metavar="step-value",
            dest='step_value', type=int, default=500,
    help=textwrap.dedent("""\
            time [in ms] waited between two frames in automatic policy play
            """ + default))

    # Play an given policy
    valid_agents= ('value-mdp', 'policy-mdp', 'qlearning')
    game_modes.add_argument("-p", "--policy", metavar="policy", dest='policy',
            type=str, choices=valid_agents,
    help=textwrap.dedent("""\
            watch the game played by a given policy. Available policies are :
            {}
            please note that a qtable must be provided for the qlearning agent
            """.format('\n'.join(['- ' + p for p in valid_agents]))))

    # --------------------------- optionnal flags ---------------------------- #
    # Generate a random map
    maps.add_argument("-g", "--random-generation", action="store_true",
            dest="random_map", help="generates a random map.")

    # Play the game interactively
    game_modes.add_argument("-i", "--interactive", action="store_true",
            dest="interactive", default=False,
            help=textwrap.dedent("""\
            plays the game interactively.
            keys to interact with the game:
                - H, Q : ←
                - J, S : ↓
                - K, Z : ↑
                - L, D : →
                - ctrl-C : quit the game
            """) + default)

    # Watch a policy step by step
    parser.add_argument("--step-by-step", action="store_true",
            dest="steps", default=False,
            help=textwrap.dedent("""\
            when watching a policy, watch it step by step
            """) + default)

    # Watch a policy with a fixed timestep between moves
    timestep.add_argument("--automatic", action="store_true",
            dest="automatic", default=True,
            help=textwrap.dedent("""\
            when watching a policy, it automatically switch to the next move
            every [x] ms, (controllable via options)
            """) + default)

    # Only winnable
    parser.add_argument("-w", "--check-winnable", action="store_true",
            dest="check_winnable", default=False,
            help=textwrap.dedent("""\
            when generating a random map, keep generating until we find one
            with a direct path from start to key, key to treasure and treasure
            to start.
            """) + default)

    # Use a text interface instead of graphical
    parser.add_argument("-t", "--text-interface", action="store_true",
            dest="text_interface", default=False,
            help=textwrap.dedent("""\
            uses a text interface instead of the graphical one.
            be carefull : works best on unix, and you need to configure
            your terminal to use the font provided in the sources
            (RobotoMono.ttf)
            """) + default)

    return parser

if __name__ == '__main__':
    parser = setup_parser()
    args = parser.parse_args()

    if not args.interactive and not args.policy:
        print("You must either play interactively [-i] or visualise a policy. [-p]")
        parser.print_help()
        exit(0)

    # ────────────────────────── create the dungeon ────────────────────────── #
    if not args.random_map and not args.map_path:
        print("You must either load a map [-l] or generate one [-g]")
        parser.print_help()
        exit(0)

    # ─────────────────────── replace agents if policy ─────────────────────── #
    advClass = Adventurer
    if args.policy:
        advClass = { 'value-mdp': ValueMDP, 'policy-mdp': PolicyMDP,
                'qlearning': AdventurerLearning }[args.policy]

    dungeon = Dungeon(args.r, args.c, 1, [advClass])

    if args.map_path:
        if args.map_path[-4:] == '.txt':
            print("The map path provided is not a valid txt file.")
            exit(0)
        dungeon.load_map(args.map_path)

    if args.check_winnable and args.random_map:
        while not dungeon.winnable:
            dungeon = Dungeon(args.r, args.c, 1, [advClass])

    # ───────────────────────── select the interface ───────────────────────── #
    interface = None
    if args.text_interface:
        interface = TextInterface(dungeon)
    else:
        interface = GraphicalInterface(dungeon)

    # ──────────────────── additional work for qlearning ───────────────────── #
    pass

    # ───────────────────────── select the game-type ───────────────────────── #
    if args.interactive:
        interface.loop()
    elif args.steps:
        interface.play_game_step()
    elif args.automatic:
        interface.play_game(args.step_value)

    # ─────────────────── print shortest paths if winnable ─────────────────── #
    # dungeon.load_map("default_map.txt")
    # winnable = interface.dungeon.winnable
    # print('Winnable ??', winnable)
    # if winnable:
        # print(interface.dungeon.display_paths())

    # ───────────────────── interactively play the game ────────────────────── #
    # interface = TextInterface(Dungeon(8, 8, 1))
    # interface.loop()

    # ────────────────── interactively play the game in GUI ────────────────── #
    # interface = GraphicalInterface(Dungeon(8, 8, 1))
    # interface.loop()

    # ────────────────────────── trying default map ────────────────────────── #
    # n, m = 2, 2
    # dungeon = Dungeon(n, m, 1, [ValueMDP])

    # dungeon.load_map('maps/default_map.txt')

    # interface = TextInterface(dungeon)
    # interface.play_game()

    # ────────────────────────────── mdp policy ────────────────────────────── #
    # n, m = 10, 18
    # dungeon = Dungeon(n, m, 1, [ValueMDP])

    # dungeon.load_map('default_map.txt')

    # interface = TextInterface(dungeon)
    # interface.play_game()
