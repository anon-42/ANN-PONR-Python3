# /usr/bin/python3
# coding=utf-8
# Replay Memory

"""
The file containing the Replay Memory class to save game stats.
"""


import pickle
import atexit
import random


class ReplayMemory:

    def __init__(self, path, length):
        self.path = path
        self.length = length
        self.memory = []
        atexit.register(self.save)
    
    def save(self):
        self.file = open(self.path, 'wb')
        pickle.dumb(memory, self.file)
        self.file.close()
    
    def get(self):
        return random.choice(self.memory)
    
    def update(self, state, new_state):
        self.memory.append([state, new_state])
        if self.length < len(self.memory):
            self.memory = self.memory[1:]
    
    def load(self):
        self.memory = pickle.load(self.path)