'''
Created on 01.02.2017

@author: Yoda
@version: 1.0

This module is for checking if the gradients are computed correctly.
'''
import numpy as np

def computeNumericalGradients(Net, inputMatrix, correctOutput):
    weightsInitial = Net.getWeights()
    numgrad = np.zeros(weightsInitial.shape)
    perturb = np.zeros(weightsInitial.shape)
    epsilon = 1e-4
    
    for p in range(len(weightsInitial)):
        # Set pertubation vector 
        perturb[p] = epsilon
        Net.setWeights(weightsInitial + perturb)
        loss2 = Net.costFunction(inputMatrix, correctOutput)
        
        Net.setWeights(weightsInitial - perturb)
        loss1 = Net.costFunction(inputMatrix, correctOutput)
        
        # Compute Numerical Gradient:
        #print((loss2 - loss1) / (2*epsilon))
        numgrad[p] = (loss2 - loss1) / (2*epsilon)
        
        # Return the value back to zero
        perturb[p] = 0
        
    #Return weights to original value:
    Net.setWeights(weightsInitial)
    
    return numgrad

def compare_gradients(Net, inputMatrix, correctOutput, pr=None):
    '''This function quantify how wrong the gradients are. Values between
    10^-8 and 10^-9 or less are OK.
    '''
    numgrad = computeNumericalGradients(Net, inputMatrix, correctOutput)
    grad = Net.computeGradients(inputMatrix, correctOutput)

    foo = np.linalg.norm(grad-numgrad) / np.linalg.norm(grad+numgrad)
    if foo <= 1e-08:
        x = True
    else:
        x = False

    return numgrad, grad, foo, x
        