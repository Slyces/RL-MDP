# encoding: utf-8
import time

import numpy as np

import kernel
import csv
from interface import LearningInterface

if __name__ == '__main__':
    game = kernel.Dungeon(8, 8)
    inter = LearningInterface(game)
    player, = game.agents

    game.load_map("default_map.txt")

    inter.display()
    q_table = player.Q
    game.reset()
    player.load_Qtable(q_table)
    a = []
    t = 0
    while len(a) < 20 or t > 2000:
        t += 1
        k = 0
        q_table = player.Q
        game.reset()
        player.load_Qtable(q_table)
        while not game.over:
            game.caption = ''
            action = player.policy()
            game.move(player, action)
            k += 1
        if player.alive:
            a.append(k)
    a = np.mean(a)
    q_table = player.Q
    game.reset()
    player.load_Qtable(q_table)
    a = []
    while len(a) < 10:
        k = 0
        q_table = player.Q
        game.reset()
        player.load_Qtable(q_table)
        while not game.over:
            game.caption = ''
            action = player.policy()
            reward = game.move(player, action)
            k +=1
        if player.alive:
            a.append(k)
    print(np.mean(a))

    for j in range(5):
        for i in range(5000):
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
                print(i + (j * 5000))
        q_table = player.Q
        game.reset()
        player.load_Qtable(q_table)
        a = []
        t = 0
        while len(a) < 20 or t > 2000:
            t += 1
            k = 0
            q_table = player.Q
            game.reset()
            player.load_Qtable(q_table)
            while not game.over:
                game.caption = ''
                action = player.policy()
                game.move(player, action)
                k += 1
            if player.alive:
                a.append(k)
        a = np.mean(a)

        path = "data/Qtable_", str((i + 1) * (j + 1)), ".csv"
        path = ''.join(path)
        path2 = "data/result_", str((i + 1) * (j + 1)), ".txt"
        path2 = ''.join(path2)
        with open(path, 'w', newline='') as csvFile:
            writer = csv.writer(csvFile)
            writer.writerows(player.Q)
        with open(path2, "w") as file:
            text = ''.join(("nombre iter pour ", str((i + 1) * (j + 1)), " : ", str(a)))
            file.write(text)



    # -------------------------- regarde le chemin --------------------------- #
    # q_table = player.Q
    # game.reset()
    # player.load_Qtable(q_table)
    # player.save_Qtable("Qtable.csv")
    # inter.play_game()
    # game.map.save_map("map.txt")