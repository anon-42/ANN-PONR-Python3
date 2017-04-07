# /usr/bin/python3
# coding=utf-8
# Main file

"""
The main file to initiate the game.
"""

from PointOfNoReturn import PONR, Interface

GAME = PONR(Interface(Interface.human, 'Spieler 1'),
            Interface(Interface.human, 'Spieler 2'))
GAME.start()
