# encoding: utf-8
import kernel
import csv
from interface import TextInterface

if __name__ == '__main__':
    game = kernel.Dungeon(2,3)
    inter = TextInterface(game)
    player, = game.agents

    for i in range(5):
        q_table = player.Q
        game.reset()
        player.load_Qtable(q_table)
        while not game.over:
            old_state = player.state
            action = player.policy()
            reward = game.move(player, action)
            new_state = player.state
            player.process_reward(old_state, new_state, action, reward)
    #inter.display()

    with open('Qtable.csv', 'w') as csvFile:
        writer = csv.writer(csvFile)
        writer.writerows(player.Q.q_table)