# /usr/bin/python3
# coding=utf-8
# Artifical Neural Net

"""
Created on 28.01.2017

This ANN is based on the following Youtube tutorial:

https://www.youtube.com/
watch?v=bxe2T-V8XRs&list=PLhODcjMcdJDoBeUBHn_6BltpCXxPbt6mw&index=1

Contains the main ANN.

@author: StrategeX
@version: beta
"""

import numpy as np
import act_func
import pickle
import gc

class Neural_Network(object):
    """
    classdocs
    """

    def __init__(self, name,  inputLayer, outputLayer, hiddenLayers=[],
                  Lambda=0.0, recurrent=None):
        """
        Constructor
        """
        # contains all necessary informations about the network
        # architecture
        self.inputLayer = inputLayer
        self.hiddenLayers = hiddenLayers
        self.outputLayer = outputLayer
        self.recurrent = recurrent

        # layer size
        self.layerSize = [inputLayer]
        for element in self.hiddenLayers:
            self.layerSize.append(element[0])
        self.layerSize.append(outputLayer[0])
        self.totalLayerNumber = len(self.layerSize)

        # random initialization of the weights
        self.weights = []
        for x in range(0, len(self.hiddenLayers)+1):
            self.weights.append(np.random.rand(self.layerSize[x]+1,
                                               self.layerSize[x+1])*2-1)

        # activation function of each layer
        self.act_func_list = [None]
        for layer in self.hiddenLayers:
            self.act_func_list.append(layer[1])
        self.act_func_list.append(self.outputLayer[1])

        #  recurrent layer
        if self.recurrent is not None:
            print('check')
            self.cloned_layer = self.recurrent[0]
            self.target_layer = self.recurrent[1]
            self.buffer = np.random.rand(self.layerSize[self.cloned_layer])
            self.weights[self.target_layer-1] = np.random.rand(
              (self.layerSize[self.taget_layer-1]
              + self.layerSize[self.cloned_layer]),
              self.layerSize[self.target_layer])
        else:
            self.cloned_layer = None
            self.target_layer = None
            self.buffer = None

        # model complexity
        self.Lambda = Lambda

        # others
        self.savecount = 0
        self.name = name

    def randomizeNet(self):
        # weights
        self.weights = []
        for x in range(0, len(self.hiddenLayers)+1):
            self.weights.append(np.random.rand(self.layerSize[x]+1,
                                               self.layerSize[x+1])*2-1)

        # recurrent layer
        if self.recurrent is not None:
            self.cloned_layer = self.recurrent[0]
            self.target_layer = self.recurrent[1]
            self.buffer = np.random.rand(self.layerSize[self.cloned_layer])
            self.weights[self.target_layer-1] = np.random.rand(
              (self.layerSize[self.taget_layer-1]
              + self.layerSize[self.cloned_layer]),
              self.layerSize[self.target_layer])


    def forward(self, inputMatrix):
        """
        This is the normal forwardpropagation function for non recurrent
        networks.
        """
        # reset
            # add bias units to input layer
        print(len(inputMatrix))
        inputMatrixb = np.ones((len(inputMatrix), self.inputLayer+1))
        inputMatrixb[:,:-1] = inputMatrix

        self.unit_input = [inputMatrixb]
        self.unit_output = [inputMatrixb]

        # new values
        for layer in range(1, self.totalLayerNumber):
            self.unit_input.append(np.dot(self.unit_output[layer-1],
                                          self.weights[layer-1]))
            # apply activation function
            foo = self.act_func_list[layer](self.unit_input[layer], 0)

            # add bias units
            foos = foo.shape
            output = np.ones((foos[0], foos[1]+1))
            output[:,:-1] = foo
            self.unit_output.append(output)
        #return without bias units
        return self.unit_output[-1][:,:-1]

    def costFunction(self, inputMatrix, correctOutput):
        """
        This shows the error of the net and that's why the output of
        this method should be as low as possible.
        """
        #self.prediction = self.forward(inputMatrix)
        su = 0
        for element in self.weights:
            su += np.sum(element**2)
        J = 0.5*np.sum((correctOutput - self.prediction)**2)/inputMatrix.shape[0]\
        + (self.Lambda/2)\
        * su
        return J

    def costFunctionPrime(self, inputMatrix, correctOutput):
        """
        This method computes the changes of the weight (derivatives)
        matrices. The learning rate is not included.
        """
        dJdW = []
        self.delta = []

        #forward
        #self.prediction = self.forward(inputMatrix)

        # backpropagation
        cfunc = self.act_func_list[-1]
        self.delta.append(np.multiply(-(correctOutput-self.prediction),
                                       cfunc(self.unit_input[-1], 1)))

        dJdW.append(np.dot(self.unit_output[-2].T,
                           self.delta[0])
                    + self.Lambda*self.weights[-1])

        for x in range(1, self.totalLayerNumber-1):
            cfunc = self.act_func_list[-(x+1)]
            self.delta.append(np.dot(self.delta[x-1], self.weights[-x][:-1,:].T)\
                                *cfunc(self.unit_input[-(x+1)], 1))
            dJdW.append(np.dot(self.unit_output[-(x+2)].T,
                                self.delta[x])\
                        + self.Lambda*self.weights[-(x+1)])

        dJdW.reverse()
        return dJdW

    def evaluate(self, inputMatrix, correctOutput):
        self.prediction = self.forward(inputMatrix)
        return self.costFunctionPrime(inputMatrix, correctOutput),\
            self.costFunction(inputMatrix, correctOutput)

    def test(self, inputMatrix, correctOutput):
        self.prediction = self.forward(inputMatrix)
        return self.costFunction(inputMatrix, correctOutput)

    def check(self):
        """
        This method show informations about the network.
        """
        print('__Network architectiture__')
        print('InputLayerSize: ', self.layerSize[0])
        for layer in range(1, self.totalLayerNumber-1):
            print('HiddenLayer' + str(layer) + 'Size', self.layerSize[layer])
        print('OutputLayerSize: ', self.layerSize[-1])
        for element in range(len(self.weights)):
            print('Weights {} to {}:'.format(element, element+1),
                  self.weights[element])
        for element in range(len(self.act_func_list)):
            print('Activation functions in layer {}:'.format(element),
                  self.act_func_list[element])

    def save(self):
        self.savecount += 1
        # work in progress (not optimal)
        save_list = [
        self.inputLayer,
        self.hiddenLayers,
        self.outputLayer,
        self.recurrent,
        self.layerSize,
        self.totalLayerNumber,
        self.weights,
        self.act_func_list,
        self.cloned_layer,
        self.target_layer,
        self.buffer,
        self.prediction,
        self.Lambda,
        self.savecount,
        self.name]

        file = open(self.name + str(self.savecount) + '.pkl', 'wb')
        pickle.dump(save_list, file)
        file.close()

    def load(self, file_name):

        file = open(file_name, 'rb')
        save_list = pickle.load(file)
        file.close()

        self.inputLayer = save_list[0]
        self.hiddenLayers = save_list[1]
        self.outputLayer = save_list[2]
        self.recurrent = save_list[3]
        self.layerSize = save_list[4]
        self.totalLayerNumber = save_list[5]
        self.weights = save_list[6]
        self.act_func_list = save_list[7]
        self.cloned_layer = save_list[8]
        self.target_layer = save_list[9]
        self.buffer = save_list[10]
        self.prediction = save_list[11]
        self.Lambda = save_list[12]
        self.savecount = save_list[13]
        self.name = save_list[14]

