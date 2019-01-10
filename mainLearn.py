# encoding: utf-8
import time

import kernel
import csv
from interface import LearningInterface

if __name__ == '__main__':
    game = kernel.Dungeon(3, 2)
    inter = LearningInterface(game)
    player, = game.agents

    #game.load_map("map.txt")
    player.load_Qtable_from_file("Qtable.csv")

    for i in range(6000):
        q_table = player.Q
        game.reset()
        player.load_Qtable(q_table)
        while not game.over:
            game.caption = ''
            old_state = player.state
            action = player.policy()
            reward = game.move(player, action)
            new_state = player.state
            player.process_reward(old_state, new_state, action, reward)
        if i % 100 == 0:
            print(i)

    # -------------------------- regarde le chemin --------------------------- #
    q_table = player.Q
    game.reset()
    player.load_Qtable(q_table)
    # inter.display()
    # time.sleep(0.5)
    # while not game.over:
        # action = player.policy()
        # game.move(player, action)
        # inter.display()
        # time.sleep(0.5)
    inter.play_game()
    game.map.save_map("map.txt")

    with open("Qtable.csv", 'w') as csvFile:
        writer = csv.writer(csvFile)
        writer.writerows(player.Q)
