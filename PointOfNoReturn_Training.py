# /usr/bin/python3
# coding=utf-8
# Point Of No Return (Training)

"""
Copy of the game file, includes only nessessary content and no graphical code.

@author: anon-42
@version: beta
"""

import numpy as np
import ann
import act_func
import trainer
import ReplayMemory as rm
import random

class Dot:

    """
    Class for the points the player can visit.
    """

    def __init__(self, x, y, state=0):
        self.x = x
        self.y = y
        self.setstate(state)

    def setstate(self, state): # -1 = bereits besucht, 0 = unbesetzt, 1 = aktuell besetzt
        """
        Sets the state of Dot.
        """
        self.state = state

    def state(self):
        """
        Returns current state of Dot.
        """
        return self.state


class PONR:

    """
    Main class of the game.
    """

    def __init__(self, P1, P2, len_x=17, len_y=9, goal=5):
        self.pos = [int(len_x / 2), int(len_y / 2)] # Position des Spielers
        self.lines_data = [np.zeros((len_x - 1) * len_y),       # waagerecht
                           np.zeros(len_x * (len_y - 1)),       # senkrecht
                           np.zeros((len_x - 1) * (len_y - 1)), # diagonal lo ru
                           np.zeros((len_x - 1) * (len_y - 1))] # diagonal ro lu
        self.touched_points = [self.pos]
        self.diagonals = []
        self.P1 = P1
        self.P2 = P2
        if len_x % 2 == len_y % 2 == goal % 2 == 1:
            self.size = [len_x, len_y]
            self.goal = goal
        else:
            raise ValueError('len_x, len_y and goal must be odd numbers.')

        self.Dots = []
        for x in range(self.size[0]):
            for y in range(self.size[1]):
                self.Dots.append(Dot(x, y))
        self.find_Dot(self.pos).setstate(1)

    def start(self):
        """
        Mainloop of the game.
        """
        while True:
            for player in [self.P1, self.P2]:
                for turn_number in range(3):
                    if self.player_turn(player,
                                        turn_number):
                        continue
                    else:
                        for turn_number in range(6):
                            self.player_turn(player,
                                             turn_number,
                                             free_kick=True)
                        if self.pos in self.touched_points:
                            if player == self.P1:
                                self.win(self.P2)
                            else:
                                self.win(self.P1)
                            return
                        break

    def find_Dot(self, pos):
        """
        Finds a Dot object in self.Dots given its coordinates and returns it.
        """
        for Dot in self.Dots:
            if Dot.x == pos[0] and Dot.y == pos[1]:
                return Dot

    def player_turn(self, player, turn_number, free_kick=False):
        """
        Executes one player turn.
        """
        prev_pos = self.pos
        prev_data = self.lines_data
        if not free_kick and not self.can_move():
            return False
        foo = [0, 0, 0, 0, 0, 0]
        foo[turn_number] = 1
        state = np.append(np.array(foo.append(int(free_kick))), self.lines_data)
        step = player.get_input(self.root, state)
        new_pos = [self.pos[0] + step[0],
                   self.pos[1] + step[1]]
        if self.pos[1] in [y for y in range((self.size[1] - self.goal) // 2,
                                            (self.size[1] + self.goal) // 2)] and self.pos[0] + step[0] == -1:
            self.win(self.P2)
        elif self.pos[1] in [y for y in range((self.size[1] - self.goal) // 2,
                                              (self.size[1] + self.goal) // 2)] and self.pos[0] + step[0] == self.size[0]:
            self.win(self.P1)
        elif not free_kick and self.rules(prev_pos, new_pos) or free_kick:
            index = (+ min(prev_pos[1], new_pos[1])
                     * (self.size[0] - 1)
                     + min(prev_pos[0], new_pos[0]))
            if step[0] == 0:        # senkrecht
                self.lines_data[1][index] = 1
            elif step[1] == 0:      # waagerecht
                self.lines_data[0][index] = 1
            elif step[0] == step[1]:# diagonal ro lu
                self.lines_data[3][index] = 1
            else:                   # diagonal lo ru
                self.lines_data[2][index] = 1
            self.pos = new_pos
            self.find_Dot(prev_pos).setstate(-1)
            self.find_Dot(new_pos).setstate(1)
            self.touched_points.append(new_pos)
            self.diagonals.append([prev_pos, new_pos])
        else:
            self.player_turn(player, turn_number, free_kick)
        return True

    def can_move(self):
        """
        Checks if the player can move.
        """
        for step in [[-1, -1], [0, -1], [1, -1], [1, 0], [1, 1], [0, 1], [-1, 1],[-1, 0]]:
            if self.rules(self.pos, [self.pos[0] + step[0], self.pos[1] + step[1]]):
                return True
        return False

    def rules(self, prev_pos, new_pos):
        """
        Checks if all rules were followed.
        """
        if (prev_pos[0] != new_pos[0]) and (prev_pos[1] != new_pos[1]):                     #"Wenn es eine Diagonale ist, dann..."
            cd = [[new_pos[0], prev_pos[1]], [prev_pos[0], new_pos[1]]]                     #cd = corresponding diagonal
            if not (cd in self.diagonals or [cd[1], cd[0]] in self.diagonals):              #"Wenn cd nicht in der Liste der bereits vorhandenen Diagonalen, dann..."
                a = True                                                                    #Regeln eingehalten; Diagonale kann gezeichnet werden
            else:
                a = False
        else:
            a = True                                                                        #Regeln eingehalten, aber es ist keine Diagonale
                                                                                            #Regeln nicht eingehalten; Diagonale darf nicht gezeichnet werden
        return ((0 <= new_pos[0] < self.size[0] and 0 <= new_pos[1] < self.size[1]) and     #Spielfeldgroesse
                (not new_pos in self.touched_points) and                                    #Betretene Punkte nicht erneut betreten
                (a))                                                                        #Kreuzen der bereits vorhandenen Diagonalen

    def reward(self, goal, penalty, new_pos, prev_pos):
        """
        Calculates a reward for a turn.
        """
        # missing: enemy goal, free kick enemy and own
        if goal == 1:
            return 1
        elif goal == -1:
        	return -1
        elif penalty == 1:
            return 0.5
        elif new_pos[0] < prev_pos[0]:
            return -0.01
        elif new_pos[0] > prev_pos[0]:
            return -0.02
        elif new_pos[0] == prev_pos[0]:
            return 0
    
    def win(self, player):
        """
        Final method of the game, is called when one player has won.
        """
        pass
    
    def game_replay(self):
        pass


class Interface:
    
    """
    The game interface to a player (human / AI).
    """

    human = 'human'
    computer = 'com'

    def __init__(self, type, name=None):
        if type in ['human', 'com']:
            self.type = type
        else:
            raise TypeError('Interface type must be "human" or "com".')
        if type == 'com':
            self.net = ann.Neural_Network(name,
                                          543,
                                          (8, act_func.tanh),
                                          [(543, act_func.tanh),
                                           (543, act_func.tanh),
                                           (543, act_func.tanh)],
                                          .0)
            self.trainer = trainer.Trainer(self.net,
                                           0.0001,
                                           0.3)
            self.rm = rm.ReplayMemory()
        self.name = name if name != None else type
        self.iterations = 0
        
    def set_step(self, step):
        """
        Sets the internal step variable.
        """
        self.step = {'KP_7': [-1, -1],
                     'KP_8': [0, -1],
                     'KP_9': [1, -1],
                     'KP_6': [1, 0],
                     'KP_3': [1, 1],
                     'KP_2': [0, 1],
                     'KP_1': [-1, 1],
                     'KP_4': [-1, 0]}[step]
        self.master.quit()

    def get_input(self, master, data):
        """
        Gets an input from the player (human or AI).
        """
        if self.type == 'human':
            self.master = master
            for event in ['<KP_7>', '<KP_8>', '<KP_9>', '<KP_6>', '<KP_3>', '<KP_2>', '<KP_1>', '<KP_4>']:
                self.master.bind(event, lambda event: self.set_step(event.keysym))
            self.master.mainloop()
        
        elif self.type == 'com':
            Qvalues = self.net.forward(data) # 8 element array
            
            # probability to choose an action ==> Boltzmann exploration
            Qvalues /= (50000/x + 0.5) # T - temperature
            
            # softmax
            e_x = np.exp(Qvalues - np.max(Qvalues))
            prob = e_x / e_x.sum()
            
            self.step = [[0, -1],
                         [1, -1],
                         [1, 0],
                         [1, 1],
                         [0, 1],
                         [-1, 1],
                         [-1, 0]][np.random.choice(np.arange(8), p=prob)]
            
            self.iterations += 1

        return self.step

    def train_net(self):
        """
        Passes the current game stats to the AI.
        """
        
        # get trainig data from replay_memory
        self.rm.number_of_turns(500)
        data = self.rm.get()
        
        state = data[0]
        action = np.array([data[1]])
        reward = np.array([[data[2]]])
        new_state = np.array([data[3]])

        for element in self.rm:
            state = np.append((state, element[0]), axis=0)
            action = np.append((action, np.array([element[1]])), axis=0)
            reward = np.append((reward, np.array([[element[2]]])), axis=0)
            new_state = np.append((new_state, np.array([element[3]])), axis=0)
        
        # compute desired output for training purposes
        correctoutput = self.net.forward(state)
        maxQ = np.amax(self.net.forward(new_state), axis=1, keepdims=True)
        
        # final state
        maxQ[np.where(np.logical_or(reward == 1, reward == -1)),:] = 0
        
        index_gamma09 = np.logical_or(np.logical_and(state[:,6]==1, 
          state[:,5]==1), np.logical_and(state[:,6]==0, state[:,2]==1))
        gamma = np.where(index_gamma09, 0.9, 1)
        gamma = np.reshape(gamma, (-1, 1))
        
        action_taken = ((action[:,1]+2)**2 + action[:,0]).flatten()
        correct_output[np.where(action_taken > 3, action_taken-1,
          action_taken)] = reward + gamma*maxQ
        
        self.trainer.train(state, correct_output, 500)

def main():
    pass