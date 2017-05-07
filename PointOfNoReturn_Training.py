# /usr/bin/python3
# coding=utf-8
# Point Of No Return (Training)

"""
Copy of the game file, includes only nessessary content and no graphical code.

@author: anon-42
@version: beta
"""

import numpy as np
import ann#artifical_neural_net as ann
import act_func as af
import trainer as tr
import replay_memory as rm
import os
import history as hs
import time
from threading import Thread
import atexit


class StopError(Exception):
    pass


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


class PONR:

    """
    Main class of the game.
    """

    def __init__(self, P1, P2, len_x=17, len_y=9, goal=5):
        self.pos = [int(len_x / 2), int(len_y / 2)] # Position des Spielers
        self.lines_data = [np.zeros((len_x - 1) * len_y),            # waagerecht
                           np.zeros(len_x * (len_y - 1)),               # senkrecht
                           np.zeros((len_x - 1) * (len_y - 1)),# diagonal lo ru
                           np.zeros((len_x - 1) * (len_y - 1))]# diagonal ro lu
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
        active, passive = self.P1, self.P2
        try:
            while True:
                for turn_number in range(3):
                    if self.player_turn(active, turn_number):
                        continue
                    else:
                        for turn_number in range(6):
                            self.player_turn(passive, turn_number, free_kick=True)
                        active, passive = passive, active
                        break
                active, passive = passive, active
                self.P1.train_net()
        except StopError:
            return


    def find_Dot(self, pos):
        """
        Finds a Dot object in self.Dots given its coordinates and returns it.
        """
        for Dot in self.Dots:
            if Dot.x == pos[0] and Dot.y == pos[1]:
                return Dot

    def player_turn(self, player, turn_number, free_kick=False, repetition=0):
        """
        Executes one player turn.
        """
        prev_pos = self.pos
        if not free_kick and not self.can_move():
            return False
        _foo = [0.0 for i in range(6)]
        _foo[turn_number] = 1.0
        _foo.append(int(free_kick))
        if player == self.P2:
            state = np.append(np.array(_foo), np.fliplr(np.array([np.concatenate(self.lines_data)])))
        else:
            state = np.append(np.array(_foo), np.concatenate(self.lines_data))
        p = player.get_input(state)
        steps = [[-1, -1], [0, -1], [1, -1], [1, 0], [1, 1], [0, 1], [-1, 1], [-1, 0]]
        if repetition <= 100:
            step = steps[np.random.choice(np.arange(8), p=p.flatten())]
        else:
            # fliplr ?
            for i in np.flip(np.argsort(p).flatten(), 0):
                step = steps[i]
                if self.rules(self.pos, [self.pos[0] + step[0], self.pos[1] + step[1]], free_kick):
                    break
        new_pos = [self.pos[0] + step[0],
                   self.pos[1] + step[1]]
        new_state = np.zeros(543)
        if turn_number == 5 and new_pos in self.touched_points:
            if player == self.P1:
                reward = -1
            else:
                reward = 1
            self.update(player, state, step, reward, new_state)
            raise StopError
        elif new_pos[1] in [y for y in range((self.size[1] - self.goal) // 2,    # goal left
                                             (self.size[1] + self.goal) // 2)] and new_pos[0] == -1:
            reward = -1
            self.update(player, state, step, reward, new_state)
            raise StopError
        elif new_pos[1] in [y for y in range((self.size[1] - self.goal) // 2,    # goal right
                                             (self.size[1] + self.goal) // 2)] and new_pos[0] == self.size[0]:
            reward = 1
            self.update(player, state, step, reward, new_state)
            raise StopError
        elif self.rules(prev_pos, new_pos, free_kick):
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
            if not 0 in step:
                self.diagonals.append([prev_pos, new_pos])
            reward = self.reward(repetition > 0, new_pos, prev_pos)
            _foo = [0.0 for i in range(6)]
            _foo[turn_number] = 1.0
            _foo.append(int(free_kick))
            if player == self.P2:
                new_state = np.append(np.array(_foo),
                                      np.fliplr(np.array([np.concatenate(self.lines_data)])))
            else:
                new_state = np.append(np.array(_foo),
                                      np.concatenate(self.lines_data))
        else:
            if repetition <= 100:
                self.player_turn(player, turn_number, free_kick, repetition+1)
                return True
            else:
                reward = self.reward(repetition > 0, new_pos, prev_pos)
        if player == self.P2:
            step = [-step[0], -step[1]]
        self.update(player, state, step, reward, new_state)
        return True

    def can_move(self):
        """
        Checks if the player can move.
        """
        for step in [[-1, -1], [0, -1], [1, -1], [1, 0], [1, 1], [0, 1], [-1, 1], [-1, 0]]:
            if self.rules(self.pos, [self.pos[0] + step[0], self.pos[1] + step[1]], False):
                return True
        if self.pos[0] in [0, self.size[1] - 1] and self.pos[1] in [y for y in range((self.size[1] - self.goal) // 2, (self.size[1] + self.goal) // 2)]:
            return True
        return False

    def rules(self, prev_pos, new_pos, free_kick):
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
                ((not new_pos in self.touched_points) or free_kick) and                                    #Betretene Punkte nicht erneut betreten
                (a or free_kick))                                                                        #Kreuzen der bereits vorhandenen Diagonalen

    def reward(self, penalty, new_pos, prev_pos):
        """
        Calculates a reward for a turn.
        """
        if penalty:
            return -0.5
        elif new_pos[0] > prev_pos[0]:
            return -0.01
        elif new_pos[0] < prev_pos[0]:
            return -0.02
        elif new_pos[0] == prev_pos[0]:
            return -0.015

    def update(self, player, state, action, reward, new_state):
        """
        TODO: add docstring
        """
        global history, rm
        rm.update(state, np.array(action), reward, new_state)
        history.add_turn([(str(int(player == self.P1)), state, np.array(action), reward)])

    def game_replay(self):
        pass


class Interface:

    """
    The game interface to a player (human / AI).
    """
    def __init__(self, name=None):
        global eta, alpha, net, history
        self.net = net
        self.trainer = tr.Trainer(self.net, eta, alpha, history)
        self.name = name if name != None else '<empty>'
        self.iterations = 0

    def get_input(self, data):
        """
        Gets an input from the ann.
        """
        global counter
        counter += 1
        Qvalues = self.net.forward(np.array([data])) # 8 element array
        self.iterations += 1
        Qvalues /= (50000/counter + 0.5) # T - temperature
        # probability to choose an action ==> Boltzmann exploration
        # softmax
        e_x = np.exp(Qvalues - np.max(Qvalues))
        prob = e_x / e_x.sum()
        return prob

    def train_net(self):
        """
        Passes the current game stats to the AI.
        """
        global number_of_turns, data_from_rm, rm
        
        # get trainig data from replay_memory
        state, action, reward, new_state = rm.get(500)

        # ---compute desired output for training purposes---
        correctoutput = self.net.forward(state)
        
        #  calculate the max Qvalue of the new state
        maxQ = np.amax(self.net.forward(new_state), axis=1, keepdims=True)
        
        # if final state, set Qvalue to 0 (so only reward matter)
        maxQ[np.where(np.logical_or(reward == 1, reward == -1))] = 0
        
        '''if a player doesn't make his/her/its last turn, the environment
        fully deterministic, that's why same actions result in same states 
        ==> discounting factor = 1
        else last turn: discounting factor = 0.9'''
        index_gamma09 = np.logical_or(np.logical_and(state[:, 6] == 1,
          state[:, 5] == 1), np.logical_and(state[:,6]==0, state[:, 2] == 1))
        gamma = np.where(index_gamma09, 0.9, 1)
        gamma = np.reshape(gamma, (-1, 1))
        
        # get the index of the action which was chosen
        action_taken = np.array([[0, 1, 2], [3, 8, 4], [5, 6, 7]], 
          dtype=np.intp)[action[:,1] + 1, action[:,0] + 1]
        
        # update Qvalues based on current experience
        correctoutput[np.arange(len(correctoutput), dtype=np.intp), 
                      action_taken] = (reward + gamma*maxQ).flatten()
        
        # use them to train ANN
        self.trainer.train(state, correctoutput, number_of_turns)
        print('train')


class Saver(Thread):

    """
    Thread for saving ANN and ReplayMemory instances once in 900 seconds.
    """

    def __init__(self, net, rm):
        Thread.__init__(self)
        self.net = net
        self.rm = rm
        self.stop = False
        atexit.register(self._stop)

    def run(self):
        """
        The threads main activity.
        """
        while not self.stop:
            self.net.save()
            self.rm.save()
            time.sleep(900)

    def _stop(self):
        """
        Prevents the thread from continuing when called.
        """
        self.stop = True


if __name__ == '__main__':
    global eta, alpha, number_of_turns, data_from_rm, rm, history, net, counter
    path = os.path.dirname(os.path.abspath(__file__)) + '/saves/'    # must end with "/" on Linux and with "\" on Windows
    history = hs.History(path + 'History')
    rm = rm.ReplayMemory(path + 'ReplayMemory.rm', 42000)
    Lambda = .0
    eta = .0001
    alpha = .7
    input_layer = 543
    output_layer = (8, af.tanh)
    hidden_layers = [(543, af.tanh),
                     (80, af.tanh)]
    number_of_turns = 500
    data_from_rm = 500
    net = ann.Neural_Network(path + 'DATA',
                             input_layer,
                             output_layer,
                             hidden_layers,
                             Lambda)
    Saver(net, rm).start()
    counter = 1
    while True:
        history.setGame(hs.generateName('main_net', 'dummy_net', 1).__next__())
        PONR(Interface('main net'), Interface('dummy net')).start()
