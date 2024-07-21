from .activation import *


"""
=> 1. Linear Forward + 2. Activation
"""
def linear_activation_forward(A_prev, W, b, activation):
    if activation == "relu":
        Z, linear_cache = linear_forward(A_prev, W, b)
        A, activation_cache = relu(Z)
    elif activation == "sigmoid":
        Z, linear_cache = linear_forward(A_prev, W, b)
        A, activation_cache = sigmoid(Z)

    cache = (linear_cache, activation_cache)

    assert(A.shape == (W.shape[0], A_prev.shape[1]))

    return A, cache


def L_model_forward(X, parameters):
    caches = []
    A = X
    L = len(parameters) // 2

    for l in range(1, L):
        A_prev = A
        A, cache = linear_activation_forward(A_prev,
                                             parameters["W"+str(l)],
                                             parameters["b"+str(l)],
                                             activation="relu")
        caches.append(cache)

    AL, cache = linear_activation_forward(A,
                                            parameters["W"+str(L)],
                                            parameters["b"+str(L)],
                                            activation="sigmoid")

    caches.append(cache)

    assert(AL.shape == (1, X.shape[1]))

    return AL, caches

