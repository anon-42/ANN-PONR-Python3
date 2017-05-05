"""
Created on 29.01.2017

@author: StrategeX
@version: 1.0
This module contains a selection of activation functions.
"""

import numpy as np

"""
The y-Parameter returns the normal function for y = 0,
otherwise the derivative.
"""
def sigmoid(x, y):
    if y == 0:
        return 1 / (1 + np.exp(-x))
    else:
        return np.exp(-x) / ((1 + np.exp(-x)) **2)

def arctan(x, y):
    if y == 0:
        return np.arctan(x)
    else:
        return 1 /(x**2 + 1)

def tanh(x, y):
    if y == 0:
        return (2 / (1 + np.exp(-2*x))) - 1
    else:
        return 1 / ((np.cosh(x))**2)
def softsign(x, y):
    if y == 0:
        return x / (1 + np.absolute(x))
    else:
        return 1 / ((1 + np.absolute(x))**2)

def identity(x, y):
    if y == 0:
        return x
    else:
        x = np.ones(x.shape)
        return x
# ------------------work in progress-----------------------------------
def _softmax(x):
    return np.exp(x) / np.sum(np.exp(x), axis=0)

def softmax(x):
    return np.apply_along_axis(_softmax, x.ndim-1, x)

