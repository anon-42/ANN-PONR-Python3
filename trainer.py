'''
Created on 02.02.2017

@author: StrategeX
This ANN is based on the following Youtube tutorial:

https://www.youtube.com/
watch?v=bxe2T-V8XRs&list=PLhODcjMcdJDoBeUBHn_6BltpCXxPbt6mw&index=1

This module uses backpropagation of error to .
'''

import numpy as np
import numgradientcheck as ngc
from matplotlib import pyplot as plt
import atexit
import pickle
import time

class Trainer(object):
    '''
    This class trains the artificial neural network using 
    backward propagation of errors with inertia term.
    
    Net -> local reference of the ANN which shall be trained
    eta -> learning rate
    alpha -> inertia term (0 <= alpha < 1)
    history -> database which is used to store the error function
    '''


    def __init__(self, Net, eta, alpha, history):

        # save error
        self.history = history
        
        # learning rate
        self.eta = eta
        
        # momentum
        self.alpha = alpha
        
        # local reference
        self.Net = Net
        
        # contains all record data
        self.data = np.array([[-1], [-1]])
        self.lesson = 0
        self.error_data_training = []
        self.error_data_test = []
        
        # makes sure to save
        atexit.register(self.__del__)
        # test if file already exist
        try:
            self.load()
        except FileNotFoundError:
            pass
        
    def load(self):
        ''' 
        Loads error function from database.
        '''
        self.data = self.history.get_error()

    def save(self):
        '''
        Stores error function in database (history).
        '''
        self.history.add_error(self.data)
        
    def train(self, inputMatrix, correctOutput,
              max_iterations, test_inputMatrix=None, 
              test_correctOutput=None):
        
        ''' 
        Method training the ANN. One method call is a lesson.
        
        inputMatrix -> 2 dimensional numpy array (shape: (size of training 
                       samples, size of input layer of ANN))
        correctOutput -> desired output 2 dimensional numpy array 
                       (shape: (size of training samples, size of input 
                       layer of ANN))
        max_iterations -> int how often gradient descent is applied with the 
                       learning rate alpha
        test_inputMatrix and test_correctOutput -> like inputMatrix and 
                       correctOutput but only for evaluation of the performance
                       of the ANN (not training on these samples)
        '''
        # for gradient comparison (testing)
        self.inputdata_tr = inputMatrix
        self.outputdata_tr = correctOutput
        
        # Make empty list to store costs:
        self.J = [-1]
        self.testJ = [-1]
        
        # stores the current changes of the weights
        self.delta = []
        
        #t1 = time.clock()
        # ----------------- first without momentum------------------------
        dJdW, cost = self.Net.evaluate(inputMatrix, correctOutput)
        
        # tracks the error function
        self.J.append(cost)
        if test_inputMatrix is not None and test_correctOutput is not None:
            self.testJ.append(self.Net.test(test_inputMatrix, 
                                            test_correctOutput))
        else:
            self.testJ.append(0)
            
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
            else:
                self.testJ.append(0)
            
            # update weights
            for x in range(0, self.Net.totalLayerNumber-1):
                self.delta.append((1-self.alpha)*self.eta*dJdW[x]\
                                    + self.alpha*self.old_delta[x])
                self.Net.weights[x] -= self.delta[-1]

            self.old_delta = self.delta
            self.delta = []

            count += 1
        # shows the time needed for a lesson
        # t2 = time.clock()
        # print('time needed: ', t2-t1, ' s')
        self.data = np.append(self.data, np.array([self.J, self.testJ]), axis=1)

        self.save()

    def chooseErrorData(self, game, lesson=None):
        ''' 
        Choose saved error function data by lesson and game name in 
        history database.
        '''
        self.history.setGame(game)
        self.load()
        if lesson is not None:
            self.error_data_training = np.split(self.data[0,:], 
                np.argwhere(self.data[0,:] == -1))[lesson][1:]
            self.error_data_test = np.split(self.data[1,:], 
                np.argwhere(self.data[1,:] == -1))[lesson][1:]
        else:
            self.error_data_training = np.delete(self.data[0,:], 
                np.argwhere(self.data[0,:]==-1))
            self.error_data_test = np.delete(self.data[1,:], 
                np.argwhere(self.data[1,:]==-1))
        
# ------------------- for test and show reasons only ---------------------- 
    def setData(self, inputMatrix, correctOutput):
        self.inputdata_tr = inputMatrix
        self.outputdata_tr = correctOutput
               
    def plot_squared_error(self):
        '''
        Shows the cost (error) function of of a training session (lesson).
        The error is calculated by this formula: 
        J = 0.5*(desiredOutput-Output)^2
        '''
        fig = plt.gcf()
        fig.canvas.set_window_title('Costfunction (Error)')
        plt.plot(self.error_data_training, label='training data')
        plt.plot(self.error_data_test, label='testing data')
        plt.grid(1)
        plt.xlabel('Iterations')
        plt.ylabel('Cost')
        plt.legend(loc='upper right')
        plt.show()

    def plot_output(self, outputneuron, inputMatrix, correctOutput,
                    points1=None, points2=None):
        ''' 
        Shows a plot which compares the desired (correct) Output with the
        actually output of a neuron.
        '''
        
        fig = plt.gcf()
        fig.canvas.set_window_title('Output')
        net_output = self.Net.forward(inputMatrix)
        x = np.arange(1, len(inputMatrix)+1)
        y = net_output[:, outputneuron-1]
        z = correctOutput[:, outputneuron-1]
        if not(points1 is None and points2 is None):
            points1 = np.arange(1, len(points1)+1)
            plt.scatter(points1, points2, 5, color='red')
        plt.plot(x, y, label='ANN output')
        plt.plot(x, z, label='Correct output')
        
        plt.xlabel('Pattern number')
        plt.ylabel('Output of neuron' + str(outputneuron))
        plt.legend(loc='lower left')
        plt.show()

    def plot_gradients(self, foo=False):
        ''' 
        Shows the difference between the computed gradients in the ANN modul 
        and the numerically calculated gradients.
        '''
        fig = plt.gcf()
        fig.canvas.set_window_title('Comparison of the computed gradients')
        numgrad, grad, qua, ok = ngc.compare_gradients(self.Net, 
                                                       self.inputdata_tr, 
                                                       self.outputdata_tr)
        print(qua, ok)
        y = numgrad-grad
        y2 = np.absolute(y)   
        plt.bar(np.arange(1,len(y)+1), y)
        plt.grid(1)
        plt.xlabel('Gradient')
        plt.ylabel('Difference')
        plt.show()

        if foo:
            print('numgrad: ', numgrad)
            print('grad: ', grad)
        print('difference: ', y)
    
    def plot_act_func(self, layer, interval):
        ''' 
        Shows activation function and its derivative of a single neuron.
        '''
        fig = plt.gcf()
        fig.canvas.set_window_title('Functions of a single neuron')
        x = np.linspace(-(interval/2), interval/2, interval*100)
        y1 = self.Net.act_func_list[layer](x, 0)
        y2 = self.Net.act_func_list[layer](x, 1)
        plt.plot(x, y1, label='activation function')
        plt.plot(x, y2, label='derivative')
        plt.xlabel('x')
        plt.ylabel('y')
        plt.legend(loc='upper left')
        plt.show()

    def plot_gradient_error_ot(self):
        '''
        experimental: first enable gerror
        '''
        
        fig = plt.gcf()
        fig.canvas.set_window_title('difference of the computed gradients'\
                                    +' over time')
        plt.plot(self.gerror, label='training data')
        plt.grid(1)
        plt.xlabel('Iterations')
        plt.ylabel('gradient error')
        plt.legend(loc='lower left')
        plt.show()
    
    def plot_changes_of_weights(self, inputMatrix, correctOutput,
              max_iterations, plot=True, test_inputMatrix=None, 
              test_correctOutput=None ):
        '''
        Shows the changes of a weights from the initially random weights
        initialization.
        '''
        wt1 = self.Net.getWeights()
        self.train(inputMatrix, correctOutput,
              max_iterations, test_inputMatrix, 
              test_correctOutput)
        wt2 = self.Net.getWeights()
        y = wt2-wt1
        count = 0
        for j in y:
            if abs(j) == 0.0:
                count += 1
                print(j)
        print(count)
        
        print(y)
        if plot:
            fig = plt.gcf()
            fig.canvas.set_window_title('Changes of the weights after'
                                        + 'training session')
            plt.bar(np.arange(1,len(y)+1), y)
            plt.grid(1)
            plt.xlabel('Weight')
            plt.ylabel('Difference')
            plt.show()
        
# -----------------------------------------------------------------------------
        
    def __del__(self):
        self.save()