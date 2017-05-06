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
import numpy as np

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
        
        # save arrays
        self.state = np.zeros((self.length, 543))
        self.action = np.zeros((self.length, 2), dtype=np.intp)
        self.reward = np.zeros((self.length, 1))
        self.new_state = np.zeros((self.length, 543))
        
        self.count = -1
        self.filledto = 0
        
        atexit.register(self.save)
        
        try:
            self.load()
        except:
            pass

    def save(self):
        """
        Saves self.memory at self.path using pickle.
        """
        file = open(self.path, 'wb')
        pickle.dump(self.__dict__, file)
        file.close()


    def get(self, number):
        """
        Returns a random element from self.memory.
        """
        index = np.random.choice(self.filledto, number)
        return self.state[index,:], self.action[index,:], self.reward[index,:],\
               self.new_state[index,:]

    def update(self, state, action, reward, new_state):
        """
        Adds a new <s,a,r,s'> element to self.memory.
        """
        self.count += 1
        if self.count >= self.length:
            self.count = 0
        
        if self.filledto <  self.length:
            self.filledto += 1
        
        self.state[self.count,:] = state
        self.action[self.count,:] = action
        self.reward[self.count,:] = reward
        self.new_state[self.count,:] =  new_state
    
    def pr_test(self):
        print('count: ', str(self.count)+'\n',
              'filledto: ', str(self.filledto)+'\n',
              'action: ', self.action)
    def load(self):
        """
        Loads an existing self.memory from self.path using pickle.
        """
        file = open(self.path, 'rb')
        instance = pickle.load(file)
        file.close()
        self.__dict__ = instance