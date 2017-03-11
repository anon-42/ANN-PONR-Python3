# Point Of No Return

import tkinter as tk
import numpy as np
#import RLAgent as agent


class Dot:

    def __init__(self, cvs, x, y, state = 0):
        self.cvs = cvs
        self.x = x
        self.y = y
        self.graphic = self.cvs.create_oval(self.x * 30 + 40,
                                            self.y * 30 + 25,
                                            self.x * 30 + 50,
                                            self.y * 30 + 35)
        self.setstate(state)

    def setstate(self, state): # 0 = unbesetzt, .5 = aktuell besetzt, 1 = bereits besucht
        self.state = state
        self.cvs.itemconfigure(self.graphic, fill = {0: 'black',
                                                     .5: 'red',
                                                     1: 'white'}[self.state])

    def state(self):
        return self.state


class Game:

    def __init__(self, P1, P2, len_x = 17, len_y = 9, goal = 5):
        self.pos = [int(len_x / 2), int(len_y / 2)] # Position des Spielers
        self.data = np.zeros((len_x - 1) * (len_y - 1) * 4 + len_x + len_y - 2) # waagerecht, senkrecht, diagonal (lo ru, ro lu)
        self.touched_points = []
        self.diagonals = []
        self.P1 = P1
        self.P2 = P2
        if len_x % 2 == len_y % 2 == goal % 2 == 1:
            self.size = [len_x, len_y]
            self.goal = goal
        else:
            raise ValueError('len_x, len_y and goal must be odd numbers.')

        self.root = tk.Tk()
        self.root.geometry(str(60 + self.size[0] * 30) + 'x' + str(30 + self.size[1] * 30))
        self.root.resizable(width = False, height = False)
        self.root.update_idletasks()
        self.cvs = tk.Canvas(self.root,
                             bg = 'white',
                             height = self.root.winfo_height(),
                             width = self.root.winfo_width())
        self.cvs.create_rectangle(0,
                                  15 + 30 * (self.size[1] - self.goal) / 2,
                                  20,
                                  15 + 30 * (self.size[1] + self.goal) / 2,
                                  fill = 'black')
        self.cvs.create_rectangle(self.root.winfo_width() - 20,
                                  15 + 30 * (self.size[1] - self.goal) / 2,
                                  self.root.winfo_width(),
                                  15 + 30 * (self.size[1] + self.goal) / 2,
                                  fill = 'black')
        self.cvs.pack()

        self.Dots = []
        for x in range(self.size[0]):
            for y in range(self.size[1]):
                self.Dots.append(Dot(self.cvs, x, y))
        self.find_Dot(self.pos).setstate(.5)
        self.root.update_idletasks()

    def start(self):
        while True:
            for player in [self.P1, self.P2]:
                for turn in range(3):
                    if self.player_turn(player):
                        continue
                    else:
                        for turn in range(6):
                            self.player_turn(player, freistoss = True)
                        break
                    self.check_for_win()

    def find_Dot(self, pos):
        for Dot in self.Dots:
            if Dot.x == pos[0] and Dot.y == pos[1]:
                return Dot

    def connect(self, pos1, pos2):
        self.cvs.create_line(45 + pos1[0] * 30,
                             30 + pos1[1] * 30,
                             45 + pos2[0] * 30,
                             30 + pos2[1] * 30,
                             width = 3)

    def player_turn(self, player, freistoss = False):
        self.root.title(player.name + ' ist am Zug')
        prev_pos = self.pos
        prev_data = self.data
        if not freistoss and not self.can_move():
            return False
        step = player.get_input(self.root)
        new_pos = [self.pos[0] + step[0],
                   self.pos[1] + step[1]]
        if not freistoss and self.rules(prev_pos, new_pos, self.touched_points, self.diagonals):
            new_data = self.data
            if step[0] == 0:
                index = (+ (self.size[0] - 1)
                         * self.size[1]
                         + min(prev_pos[1], new_pos[1])
                         * self.size[0]
                         + prev_pos[0])
            elif step[1] == 0:          # waagerecht
                index = (+ prev_pos[1]
                         * (self.size[0] - 1)
                         + min(prev_pos[0], new_pos[0]))
            else:                       # diagonal
                index = (+ (self.size[0] - 1)
                         * self.size[1]
                         + (self.size[1] - 1)
                         * self.size[0])
                if step[0] == step[1]:  # ro lu
                    index += (+ (self.size[0] - 1)
                              * (self.size[1] - 1)
                              + min(prev_pos[1], new_pos[1])
                              * self.size[0]
                              + min(prev_pos[0], new_pos[0]))
                else:                   # lo ru
                    index += (+ min(prev_pos[1], new_pos[1])
                              * self.size[0]
                              + min(prev_pos[0], new_pos[0]))
            new_data[index] = 1
            self.pos = new_pos
            self.data = new_data
            self.find_Dot(prev_pos).setstate(1)
            self.find_Dot(new_pos).setstate(.5)
            self.connect(prev_pos, new_pos)
            self.touched_points.append(new_pos)
            self.diagonals.append([prev_pos, new_pos])
            self.root.update_idletasks()
        elif freistoss:
            self.pos = new_pos
            self.find_Dot(prev_pos).setstate(1)
            self.find_Dot(new_pos).setstate(.5)
            self.connect(prev_pos, new_pos)
            self.root.update_idletasks()
        else:
            self.player_turn(player)
        return True

    def can_move(self):
        return True in map(lambda x: x != False,
                           [self.rules(self.pos,
                                       step,
                                       self.touched_points,
                                       self.diagonals) for step in [[-1, -1],
                                                                    [ 0, -1],
                                                                    [ 1, -1],
                                                                    [ 1,  0],
                                                                    [ 1,  1],
                                                                    [ 0,  1],
                                                                    [-1,  1],
                                                                    [-1,  0]]])

    def check_for_win(self):
        return self.pos in [[0, goal] for goal in range(0)] + [[self.size[0], goal] for goal in range(0)]

    def rules(self, prev_pos, new_pos, touched_points, diagonals):
        if (prev_pos[0] != new_pos[0]) and (prev_pos[1] != new_pos[1]):                     #"Wenn es eine Diagonale ist, dann..."
            cd = [[new_pos[0], prev_pos[1]], [prev_pos[0], new_pos[1]]]                     #cd = corresponding diagonal
            if not (cd in diagonals or [cd[1], cd[0]] in diagonals):                        #"Wenn cd nicht in der Liste der bereits vorhandenen Diagonalen, dann..."
                a = True                                                                    #Regeln eingehalten; Diagonale kann gezeichnet werden
            else:
                a = False
        else:
            a = True                                                                        #Regeln eingehalten, aber es ist keine Diagonale
                                                                                            #Regeln nicht eingehalten; Diagonale darf nicht gezeichnet werden
        return ((0 <= new_pos[0] <= self.size[0] and 0 <= new_pos[1] <= self.size[1]) and   #Spielfeldgroesse
                (not new_pos in touched_points) and                                         #Betretene Punkte nicht erneut betreten
                (a))                                                                        #Kreuzen der bereits vorhandenen Diagonalen

    def reward(self):
        pass


class Interface:

    human = 'human'
    computer = 'com'

    def __init__(self, type, name = None):
        if type in ['human', 'com']:
            self.type = type
        else:
            raise TypeError('Interface type must be "human" or "com".')
        self.name = name if name != None else type

    def set_step(self, step):
        self.step = {'KP_7': [-1, -1],
                     'KP_8': [ 0, -1],
                     'KP_9': [ 1, -1],
                     'KP_6': [ 1,  0],
                     'KP_3': [ 1,  1],
                     'KP_2': [ 0,  1],
                     'KP_1': [-1,  1],
                     'KP_4': [-1,  0]}[step]
        self.master.quit()

    def get_input(self, master):
        self.master = master
        if self.type == 'human':
            for event in ['<KP_7>', '<KP_8>', '<KP_9>', '<KP_6>', '<KP_3>', '<KP_2>', '<KP_1>', '<KP_4>']:
                self.master.bind(event, lambda event: self.set_step(event.keysym))
            self.master.mainloop()
        elif self.type == 'com':
            #agent.getinput()
            pass
        return self.step

    def return_info(self, data):
        pass ## Infos an Netz weitergeben


if __name__ == '__main__':
    foo = Game(Interface(Interface.human, 'Spieler 1'),
               Interface(Interface.human, 'Spieler 2'))
    foo.start()
