# encoding: utf-8
import time, kernel, csv, numpy as np
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
    while len(a) < 20 and t < 10000:
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
            print(k)
    ratio = len(a) / t
    print("ratio", ratio)
    a = np.mean(a)
    print(a)

    with open("data/initial.txt", "w") as file:
        file.write(''.join(("ratio : ", str(ratio), "\n")))
        file.write(''.join(("nombre iter : ", str(a))))


    for j in range(30):
        for i in range(2000):
            q_table = player.Q
            game.reset()
            player.load_Qtable(q_table)
            t = 0
            while not game.over and t <= 2000:
                t +=1
                game.caption = ''
                old_state = player.state
                action = player.policy()
                reward = game.move(player, action)
                new_state = player.state
                player.process_reward(old_state, new_state, action, reward)
            if i % 100 == 0:
                print(i + (j * 1000))
            if t == 2000:
                print("t")
        q_table = player.Q
        game.reset()
        player.load_Qtable(q_table)
        a = []
        t = 0
        while len(a) < 20 and t < 10000:
            t += 1
            k = 0
            q_table = player.Q
            game.reset()
            player.load_Qtable(q_table)
            while not game.over and k <= 2000:
                game.caption = ''
                action = player.policy()
                game.move(player, action)
                k += 1
            if player.alive and k < 2000:
                a.append(k)
                print("ok")
            if k == 2000:
                print("k")
        ratio = len(a) / t
        a = np.mean(a)

        path = "data/Qtable_", str((i + 1) * (j + 1)), ".csv"
        path = ''.join(path)
        path2 = "data/result_", str((i + 1) * (j + 1)), ".txt"
        path2 = ''.join(path2)
        with open(path, 'w', newline='') as csvFile:
            writer = csv.writer(csvFile)
            writer.writerows(player.Q)
        with open(path2, "w") as file:
            text = ''.join(("nombre iter pour ", str((i + 1) * (j + 1)), " : ", str(a),"\n"))
            file.write(text)
            file.write(''.join(("ratio : ", str(ratio))))
            print("ratio", ratio)



    # -------------------------- regarde le chemin --------------------------- #
    # q_table = player.Q
    # game.reset()
    # player.load_Qtable(q_table)
    # player.save_Qtable("Qtable.csv")
    # inter.play_game()
    # game.map.save_map("map.txt")
