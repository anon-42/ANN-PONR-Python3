# /usr/bin/python3
# coding=utf-8
# Replay Memory

"""
The file containing the Replay Memory class to save game stats.

@author: anon-42
@version: beta
"""


import pickle
import atexit
import random


class ReplayMemory:

    def __init__(self, path, length):
        self.path = path
        self.length = length
        self.memory = []
        self.count = 0
        atexit.register(self.save)

    def __iter__(self):
        return self

    def __next__(self):
        if self.count < self.number:
            self.count += 1
            return random.choice(self.memory)
        else:
            self.count = 0
            raise StopIteration

    def number_of_turns(self, number):
        self.number = number

    def save(self):
        self.file = open(self.path, 'wb')
        pickle.dump(self.memory, self.file)
        self.file.close()

    def get(self):
        return random.choice(self.memory)

    def update(self, state, action, reward, new_state):
        self.memory.append([state, action, reward, new_state])
        if self.length < len(self.memory):
            self.memory = self.memory[1:]

    def load(self):
        self.memory = pickle.load(self.path)
