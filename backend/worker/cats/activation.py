import numpy as np


"""
1. Linear Forward
"""
def linear_forward(A, W, b):
    Z = np.dot(W, A) + b

    assert(Z.shape == (W.shape[0], A.shape[1]))
    cache = (A, W, b)

    return Z, cache


"""
2-1. Activation - ReLU function; g(z) = max(0,z)
"""
def relu(Z):
    A = np.maximum(0, Z)
    cache = Z
    assert(A.shape == Z.shape)

    return A, cache


"""
2-2. Activation - Sigmoid function; g(z) =  1/(1+e^(-z))
"""
def sigmoid(Z):
    A = 1/(1+np.exp(-Z))
    cache = Z
    assert(A.shape == Z.shape)

    return A, cache



"""
3-1. ReLU Backward
"""
def relu_backward(dA, activation_cache):
    Z = activation_cache
    dZ = np.array(dA, copy=True)

    dZ[Z <= 0] = 0

    assert(dZ.shape == Z.shape)

    return dZ

"""
3-2. Sigmoid Backward
"""
def sigmoid_backward(dA, activation_cache):
    Z = activation_cache

    s = 1/(1 + np.exp(-Z))
    dZ = dA * s * (1-s)

    assert(dZ.shape == Z.shape)

    return dZ


"""
4. Linear Backward
"""
def linear_backward(dZ, cache):
    A_prev, W, b = cache
    m = A_prev.shape[1]

    dW = 1./m * np.dot(dZ, A_prev.T)
    db = 1./m * np.sum(dZ, axis=1, keepdims=True)
    dA_prev = np.dot(W.T, dZ)

    assert (dA_prev.shape == A_prev.shape)
    assert (dW.shape == W.shape)
    assert (db.shape == b.shape)

    return dA_prev, dW, db

