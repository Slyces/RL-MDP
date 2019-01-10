# encoding: utf-8
import time

import kernel
import csv
from interface import TextInterface

if __name__ == '__main__':
    game = kernel.Dungeon(4,4)
    inter = TextInterface(game)
    player, = game.agents

    for i in range(500):
        q_table = player.Q
        game.reset()
        player.load_Qtable(q_table)
        while not game.over:
            old_state = player.state
            action = player.policy()
            reward = game.move(player, action)
            new_state = player.state
            player.process_reward(old_state, new_state, action, reward)
        if i % 100 == 0:
            print(i)

    #regarde le chemin
    q_table = player.Q
    game.reset()
    player.load_Qtable(q_table)
    inter.display()
    time.sleep(2)
    while not game.over:
        action = player.policy()
        game.move(player, action)
        inter.display()
        time.sleep(2)

    with open("Qtable.csv", 'w') as csvFile:
        writer = csv.writer(csvFile)
        writer.writerows(player.Q)