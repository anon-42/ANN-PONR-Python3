# /usr/bin/python3
# coding=utf-8
# Point Of No Return

"""
The game file, contains the game and the interface to the players.

@author: anon-42
@version: beta
"""

import tkinter as tk
import numpy as np
import ann
import act_func
import time


class Dot:

    """
    Class for the points the player can visit.
    """

    def __init__(self, cvs, x, y, state=0):
        self.cvs = cvs
        self.x = x
        self.y = y
        self.graphic = self.cvs.create_oval(self.x * 30 + 40,
                                            self.y * 30 + 25,
                                            self.x * 30 + 50,
                                            self.y * 30 + 35)
        self.setstate(state)

    def setstate(self, state): # -1 = bereits besucht, 0 = unbesetzt, 1 = aktuell besetzt
        """
        Sets the state of Dot.
        """
        self.state = state
        self.cvs.itemconfigure(self.graphic, fill={-1: 'black',
                                                   0: 'white',
                                                   1: 'red'}[self.state])


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
        if self.P2.type == 'com':
            raise TypeError('Player 2 (second argument of PONR.__init__) must have type "human".')
        elif self.P1.type == 'com':
            explanation_text = 'Sie ({}) spielen auf das linke Tor.'.format(self.P2.name)
        else:
            explanation_text = '{} spielt auf das rechte, {} auf das linke Tor.'.format(self.P1.name, self.P2.name)

        self.root = tk.Tk()
        self.root.geometry(str(60 + self.size[0] * 30) + 'x' + str(60 + self.size[1] * 30))
        self.root.resizable(width=False, height=False)
        self.root.update_idletasks()
        self.explanation = tk.Label(self.root,
                                    width=self.root.winfo_width(),
                                    bg='white',
                                    font='Verdana 15',
                                    text=explanation_text)
        self.cvs = tk.Canvas(self.root,
                             bg='white',
                             height=self.root.winfo_height() - self.explanation.winfo_height(),
                             width=self.root.winfo_width())
        self.cvs.create_rectangle(0,
                                  15 + 30 * (self.size[1] - self.goal) / 2,
                                  20,
                                  15 + 30 * (self.size[1] + self.goal) / 2,
                                  fill='black')
        self.cvs.create_rectangle(self.root.winfo_width() - 20,
                                  15 + 30 * (self.size[1] - self.goal) / 2,
                                  self.root.winfo_width(),
                                  15 + 30 * (self.size[1] + self.goal) / 2,
                                  fill='black')
        self.explanation.pack()
        self.cvs.pack(pady=2)

        self.Dots = []
        for x in range(self.size[0]):
            for y in range(self.size[1]):
                self.Dots.append(Dot(self.cvs, x, y))
        self.find_Dot(self.pos).setstate(1)
        self.root.update_idletasks()

    def start(self):
        """
        Mainloop of the game.
        """
        active, passive = self.P1, self.P2
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

    def find_Dot(self, pos):
        """
        Finds a Dot object in self.Dots given its coordinates and returns it.
        """
        for Dot in self.Dots:
            if Dot.x == pos[0] and Dot.y == pos[1]:
                return Dot

    def connect(self, pos1, pos2):
        """
        Draws a line to connect two dots.
        """
        self.cvs.create_line(45 + pos1[0] * 30,
                             30 + pos1[1] * 30,
                             45 + pos2[0] * 30,
                             30 + pos2[1] * 30,
                             width=3)

    def player_turn(self, player, turn_number, free_kick=False):
        """
        Executes one player turn.
        """
        if not free_kick:
            self.root.title(player.name + ' ist am Zug')
        else:
            self.root.title('Freistoß für ' + player.name)
        prev_pos = self.pos
        if not free_kick and not self.can_move():
            return False
        _foo = [0, 0, 0, 0, 0, 0]
        _foo[turn_number] = 1
        _foo.append(int(free_kick))
        step = player.get_input(self.root,
                                np.append(np.array(_foo), np.concatenate(self.lines_data)))
        if player.type == 'com':
            Qvalues = list(step.keys())
            Qvalues.sort(reverse=True)
            while len(Qvalues) > 0:
                if self.rules(self.pos, [self.pos[0] + step[Qvalues[0]][0], self.pos[1] + step[Qvalues[0]][1]], free_kick):
                    step = step[Qvalues[0]]
                    break
                else:
                    Qvalues = Qvalues[1:]
        new_pos = [self.pos[0] + step[0],
                   self.pos[1] + step[1]]
        if turn_number == 5 and new_pos in self.touched_points:
            if player == self.P1:
                self.win(self.P2)
            else:
                self.win(self.P1)
        elif new_pos[1] in [y for y in range((self.size[1] - self.goal) // 2,
                                             (self.size[1] + self.goal) // 2)] and new_pos[0] == -1:
            self.win(self.P2)
        elif new_pos[1] in [y for y in range((self.size[1] - self.goal) // 2,
                                             (self.size[1] + self.goal) // 2)] and new_pos[0] == self.size[0]:
            self.win(self.P1)
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
            self.connect(prev_pos, new_pos)
            self.touched_points.append(new_pos)
            self.diagonals.append([prev_pos, new_pos])
            self.root.update_idletasks()
        else:
            self.player_turn(player, turn_number, free_kick)
        return True

    def can_move(self):
        """
        Checks if the player can move.
        """
        for step in [[-1, -1], [0, -1], [1, -1], [1, 0], [1, 1], [0, 1], [-1, 1], [-1, 0]]:
            if self.rules(self.pos, [self.pos[0] + step[0], self.pos[1] + step[1]], False):
                return True
        if self.pos[0] in [0, self.size[0]] and self.pos[1] in [y for y in range((self.size[1] - self.goal) // 2, (self.size[1] + self.goal) // 2)]:
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
        return (((0 <= new_pos[0] < self.size[0] and 0 <= new_pos[1] < self.size[1]) or
                (new_pos[0] in [-1, self.size[0]] and new_pos[1] in [y for y in range((self.size[1] - self.goal) // 2, (self.size[1] + self.goal) // 2)])) and	 #Spielfeldgroesse
                ((not new_pos in self.touched_points) or free_kick) and									#Betretene Punkte nicht erneut betreten
                (a or free_kick))                                                                  #Kreuzen der bereits vorhandenen Diagonalen

    def win(self, player):
        """
        Final method of the game, is called when one player has won.
        """
        self.root.destroy()
        win_msg = tk.Tk()
        win_msg.title('Ende')
        win_msg.geometry('200x100')
        tk.Label(win_msg,
                 text='{} hat gewonnen!'.format(player.name)).place(x=100, y=25, anchor=tk.CENTER)
        tk.Button(win_msg,
                  text='Spielverlauf ansehen',
                  command=self.game_replay).place(x=100, y=50, anchor=tk.CENTER) # TODO: implement self.game_replay
        tk.Button(win_msg,
                  text='Schließen',
                  command=win_msg.destroy).place(x=100, y=80, anchor=tk.CENTER)
        win_msg.mainloop()

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
                                          .0,
                                          readonly=True)
            self.net.load('/media/lukas/BA87-AB98/Schule/SFA 17 KNN/Softwareprodukt/trained-ANNs/DATA11.net')
        self.name = name if name != None else type

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
            Qvalues = self.net.forward(np.array([data])) # 8 element array
            # self.step = [[-1, -1],
            #              [0, -1],
            #              [1, -1],
            #              [1, 0],
            #              [1, 1],
            #              [0, 1],
            #              [-1, 1],
            #              [-1, 0]][np.argmax(Qvalues)]
            self.step = dict(zip(Qvalues.tolist()[0], [[-1, -1], [0, -1], [1, -1], [1, 0], [1, 1], [0, 1], [-1, 1], [-1, 0]]))
            time.sleep(.5)
        return self.step
