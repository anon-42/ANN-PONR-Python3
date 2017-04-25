'''
Created on 02.02.2017

@author: StrategeX
This ANN is based on the following Youtube tutorial:

https://www.youtube.com/
watch?v=bxe2T-V8XRs&list=PLhODcjMcdJDoBeUBHn_6BltpCXxPbt6mw&index=1

This module uses scipy optimize package to train the ANN via backpropagation.
'''

import numpy as np
from scipy import optimize as opt
import numgradientcheck as ngc

class Trainer(object):
    '''
    This Class trains the artificial neural network using the BSGF
    algorithm which is already implemented in scipy.
    '''


    def __init__(self, Net, eta, alpha):
        '''
        Makes a local reference to Neural Network.
        '''

        # learning rate
        self.eta = eta

        # momentum
        self.alpha = alpha

        # local reference
        self.Net = Net


    def train(self, inputMatrix, correctOutput,
              max_iterations, test_inputMatrix=None,
              test_correctOutput=None):

        # Make empty list to store costs:
        self.J = []
        self.testJ = []

        # stores the current changes of the weights
        self.delta = []

        # ----------------- first without momentum------------------------
        dJdW, cost = self.Net.evaluate(inputMatrix, correctOutput)
        # tracks the error function
        self.J.append(cost)
        if test_inputMatrix is not None and test_correctOutput is not None:
            self.testJ.append(self.Net.test(test_inputMatrix,
                                            test_correctOutput))

        # update weights
        for x in range(0, self.Net.totalLayerNumber-1):
            self.delta.append(self.eta*dJdW[x])
            self.Net.weights[x] -= self.delta[-1]

        self.old_delta = self.delta
        self.delta = []

        # ----------------- secound, third ... with momentum-----------------
        count = 2
        while count <= max_iterations:
            dJdW, cost = self.Net.evaluate(inputMatrix, correctOutput)

            # tracks the error function
            self.J.append(cost)
            if test_inputMatrix is not None and test_correctOutput is not None:
                self.testJ.append(self.Net.test(test_inputMatrix,
                                            test_correctOutput))

            # update weights
            for x in range(0, self.Net.totalLayerNumber-1):
                self.delta.append((1-self.alpha)*self.eta*dJdW[x]\
                                    + self.alpha*self.old_delta[x])
                self.Net.weights[x] -= self.delta[-1]

            self.old_delta = self.delta
            self.delta = []

            count += 1

