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

    """
    Class for managing <s,a,r,s'> training elements.\n
    Parameters:\n
        path -> where content will be saved at exit.
        length -> maximum number of elements saved in the memory.
    """

    def __init__(self, path, length):
        self.path = path
        self.length = length
        self.memory = []
        self.count = 0
        atexit.register(self.save)
        try:
            self.load()
        except:
            pass

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
        """
        Sets the number of elements from self.memory returned by self.__iter__().
        """
        self.number = number

    def save(self):
        """
        Saves self.memory at self.path using pickle.
        """
        self.file = open(self.path, 'wb')
        pickle.dump(self.memory, self.file)
        self.file.close()

    def get(self):
        """
        Returns a random element from self.memory.
        """
        return random.choice(self.memory)

    def update(self, state, action, reward, new_state):
        """
        Adds a new <s,a,r,s'> element to self.memory.
        """
        self.memory.append([state, action, reward, new_state])
        if self.length < len(self.memory):
            self.memory = self.memory[1:]

    def load(self):
        """
        Loads an existing self.memory from self.path using pickle.
        """
        self.memory = pickle.load(open(self.path, 'rb'))
