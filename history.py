'''
Created on 22.02.2017

@author: StrategeX
@version: 1.0
'''

import sqlite3
import numpy as np
import io
import atexit
import datetime
import uuid

class NoTurnLeftException(Exception):
    def __init__(self, c_turn):
        self.c_turn = c_turn
        print('You have reached the maximunm of saved turns.')

class generateName():
    def __init__(self, player1, player2, numberOfGames):
        self.player1 = player1
        self.player2 = player2
        self.numberOfGames = numberOfGames
        self.c_it = 1
        
    def __iter__(self):
        self.c_it = 1
        return self
    
    def __next__(self):
        if self.c_it <= self.numberOfGames:
            self.c_it += 1
            now = datetime.datetime.now()
            return self.player1\
            + '_vs_'\
            + self.player2\
            +'__dt-{}_{:02d}_{:02d}_{:02d}_{:02d}_{:02d}_{:06d}'\
            .format(now.year, now.month, now.day, now.hour, now.minute,
                    now.second, now.microsecond)\
            + '__id-'+ str(uuid.uuid4())
            
            
        else:
            raise StopIteration
                       
class History(object):
    '''
    classdocs
    '''


    def __init__(self, name='history'):
        '''
        Constructor
        '''
        # counts the number of turns in a game
        self.counter = 1
        
        # refer to the next turn
        self.c_turn = 2
        
        # names for saving etc.
        self.name = name
        self.game = 'default_setting'
        
        #create database
        self.connection = sqlite3.connect(self.name+'.db', 
          detect_types=sqlite3.PARSE_DECLTYPES)
        self.cursor = self.connection.cursor()
        
        # define array data type
        sqlite3.register_adapter(np.ndarray, self.__adapt_array)
        sqlite3.register_converter('ARRAY', self.__convert_array)
        
        # create table
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS games (
            game TEXT, turns INTEGER)''')
        
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS default_setting (
            number INTEGER UNIQUE, 
            player TEXT, state ARRAY,
            action ARRAY, reward INTEGER)''')
        
        
        
        # makes sure to save
        atexit.register(self.__del__)
        
    def add_turn(self, data_list):
        ''' 
        data_list = [(player, state, action, reward), ...]
        ''' 
        # insert
        try:
            for row in data_list:
                values = (self.counter,) + row
                sql = 'INSERT INTO {} VALUES (?, ?, ?, ?, ?)'.format(self.game)
                with self.connection:
                    self.cursor.execute(sql, values)
                        # maybe 
                        #self.connection.commit
                    self.counter += 1  
                 
        except:
            print('Problem: Could not insert the transition.')
    
    def __adapt_array(self, arr):
        """
        https://stackoverflow.com/
        questions/18621513/python-insert-numpy-array-into-sqlite3-database
        """
        out = io.BytesIO()
        np.save(out, arr)
        out.seek(0)
        return sqlite3.Binary(out.read())

    def __convert_array(self, text):
        '''
        https://stackoverflow.com/
        questions/18621513/python-insert-numpy-array-into-sqlite3-database
        '''
        out = io.BytesIO(text)
        out.seek(0)
        return np.load(out)
    
    def setGame(self, game):
        ''' 
        Set the name of the current game. If the game does not exist,
        it creates a new one.
        '''
        with self.connection:
            self.cursor.execute("UPDATE games SET turns=? WHERE game=?",
                                (self.counter, self.game))
 
            self.cursor.execute("SELECT turns FROM games WHERE game = ?", 
                                (game,))
            data = self.cursor.fetchone()
            
            # not in database and not current game ==> new game
            if data is None and self.game != game:
                self.counter = 1
                self.c_turn = 1
                self.game = game
                self.cursor.execute('''INSERT INTO games VALUES (?, ?)''', 
                                    (self.game, self.counter))
                
                # create table
                self.cursor.execute('''CREATE TABLE IF NOT EXISTS {} (
                    number INTEGER UNIQUE, 
                    player TEXT, state ARRAY,
                    action ARRAY, reward INTEGER)'''\
                    .format(self.game))

            # current game ==> set current turn to 1
            elif self.game == game:
                self.c_turn = 1
            
            # entry in database and not current game ==> switch to
            elif data is not None:
                self.game = game
                self.counter = data[0]
                self.c_turn = 1
    
    def setTurn(self, turn=1):
        self.c_turn = turn

    def get_next_turn(self, player=None):
        try:
            if player is None:
                with self.connection:
                    
                    # player, state, action, reward
                    self.cursor.execute('''
                        SELECT number, player, state, action, reward FROM {}
                        WHERE number=?
                    '''.format(self.game), (self.c_turn,))
                    
                    foo = self.cursor.fetchone()
                    if foo is None:
                        raise NoTurnLeftException(self.c_turn)
                    player = foo[1]
                    # next_state
                    self.c_turn += 1
                    self.cursor.execute('''
                        SELECT number, player, state, action, reward FROM {}
                        WHERE number BETWEEN (?) AND (?) AND player=(?)
                    '''.format(self.game), (self.c_turn, self.c_turn+7, player))
                    bar = self.cursor.fetchall()
                    if not bar:
                        raise NoTurnLeftException(self.c_turn)
                    bar = bar[0]
                    end = foo[1:] + (bar[2],)
                
                return end
            else:
                with self.connection:
                    # player, state, action, reward
                    self.cursor.execute('''
                        SELECT number, player, state, action, reward FROM {}
                        WHERE number BETWEEN (?) AND (?) AND player=(?)
                    '''.format(self.game), 
                    (self.c_turn, self.c_turn+7, player))
                    foo = self.cursor.fetchall()
                    if not foo:
                        raise NoTurnLeftException(self.c_turn)
                    foo = foo[0]
                    
                    # next_state
                    next_turn = foo[0] + 1
                    self.cursor.execute('''
                        SELECT number, player, state, action, reward FROM {}
                        WHERE number BETWEEN (?) AND (?) AND player=(?)
                    '''.format(self.game), (next_turn, next_turn+7, player))

                    bar = self.cursor.fetchall()
                    if not bar:
                        raise NoTurnLeftException(self.c_turn)
                    bar = bar[0]
                    self.c_turn = bar[0]
                    end = foo[1:] + (bar[2],)
                    
                return end
        except KeyboardInterrupt:
            return None
        
    def pr_next_turn(self, player=None):
        player, state, action, reward, next_state = self.get_next_turn(player)
        print('| {:6} | {:25} ... {:25} | {:25} ... {:25} | {:25} | {:25} ... {:25} |'\
            .format(player,
            state[1], state[-1], action[1], 
            action[-1], reward, next_state[1], next_state[-1]))
        
    def deleteGame(self, game):
        with self.connection:
            self.cursor.execute('''DELETE FROM games WHERE game=(?)''', 
                                (self.game,))
            self.cursor.execute('''DROP TABLE {}'''\
                                .format(self.game))
    
    def renameGame(self, new, old):
        self.cursor.execute('''ALTER TABLE {} RENAME TO {}'''.format(old, new))
                 
    def pr_all(self, gamesonly=None):
        '''
        Not recommended. For test purposes only.
        '''
        self.cursor.execute('SELECT game from games')
        games = self.cursor.fetchall()
        if gamesonly is None:
            for x in games:
                print('')
                print(x[0])
                print('-'*163)
                self.cursor.execute('SELECT * from {}'.format(x[0]))
                foo = self.cursor.fetchall()
                if foo:
                    for number, player, state, action, reward in foo:
                        print('| {:6} | {:6} | {:25} ... {:25} | {:25} ... {:25} | {:25} |'\
                              .format(number, player,
                                      state[1], state[-1], action[1], action[-1], reward))
                
        self.cursor.execute('SELECT * from games')
        foo = self.cursor.fetchall()
        if foo:
            for game, turns in foo:
                print('| {:10} | {:10} |'.format(game, turns))
    
    def __add__(self, other):
        '''
        This magical method overloads the + operator and makes the user able
        to easily attach tables from one database to another.
        '''
        with self.connection:
            # test
            self.pr_all()
            other.pr_all('no')
            other.cursor.execute('''SELECT game FROM games''')
            game_list = other.cursor.fetchall()
            self.cursor.execute("""ATTACH DATABASE '{}' AS 'tocopy'"""\
                                .format(self.name + '.db'))
            print(game_list)
            for element in game_list:
                element = element[0]
                self.cursor.execute('''SELECT EXISTS(SELECT 1 FROM games 
                                             WHERE game='{}' LIMIT 1)'''\
                            .format(element))
                
                # check if game already exist
                exist = self.cursor.fetchone()[0]
                if not exist:
                    self.setGame(element)
                    other.cursor.execute('''SELECT player, state,
                                         action, reward FROM {}'''\
                                         .format(element))
                    data = other.cursor.fetchall()
                    self.add_turn(data)
                else:
                    print('Could not insert {} because'.format(element)
                    + ' a game with the same name'\
                    + ' already exist. Please rename and try again.')
            
            self.cursor.execute("""DETACH DATABASE 'tocopy'""")
                    
    def __del__(self):
        with self.connection:
            self.cursor.execute("UPDATE games SET turns=? WHERE game=?",
                                (self.counter, self.game))
        