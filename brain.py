import numpy as np
import math
import matplotlib.pyplot as plt



def get_dataset(rows):
    """Méthode poyr générer le dataset"""
    sick=np.random.rand(rows,2)+np.array([-2,-2])
    healthy=np.random.rand(rows,2)+np.array([2,2])
    features=np.vstack([sick,healthy])
    targets=np.concatenate((np.zeros(rows), np.zeros(rows)+1))
    #plt.plot(sick, 'ro')
    #plt.plot(healthy, 'bx')
    #plt.plot(features, 'g^')
    #plt.show()
    return features, targets

def init_variables():
    """Init variables (weights, bias)"""
    weights=np.random.normal(size=2)
    bias=0
    return(weights,bias)

def pre_activation(features, weights, bias):
    """Compute pre activation"""
    return np.dot(features,weights)+bias

def activation(z):
    """Compute activation"""
    return 1/(1+np.exp(-z))

features,targets=get_dataset(5)
print(features, targets)
weights,bias=init_variables()
print(weights, bias)
z=pre_activation(features, weights, bias)
print(z)
a=activation(z)
print(a)
