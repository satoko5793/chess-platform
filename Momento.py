import numpy as np
import os

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