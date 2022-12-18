import numpy as np
import os
import json


def save(filepath, board):
    current_directory = os.path.dirname(os.path.abspath(__file__))
    print(current_directory)
    os.chdir(filepath)
    memo = np.array(board)
    print(memo)
    np.save('memo.npy', memo)
    os.chdir(current_directory)

def load(filepath):
    memo = np.load(filepath)
    board = memo.tolist()
    print(memo)
    return board


class LookBack:
    def __init__(self):
        self.moves = []

    def add_move(self, player, col, row):
        self.moves.append([player,col,row])

    def delete_move(self, num):
        if len(self.moves) >= num:
            self.moves = self.moves[:-num]
        else:
            print("错误调用delete_move函数")

    def save(self, file='history.json'):
        with open(file, 'w') as f:
            json.dump(self.moves, f)

    def load(self, file='history.json'):
        with open('history.json', 'r') as f:
            self.moves = json.load(f)