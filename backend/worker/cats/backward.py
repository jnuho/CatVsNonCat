from .activation import *


"""
=> 3. Backward + 4. Linear Backward
"""
def linear_activation_backward(dA, cache, activation):
    linear_cache, activation_cache = cache

    if activation == "sigmoid":
        dZ = sigmoid_backward(dA, activation_cache)
        dA_prev, dW, db = linear_backward(dZ, linear_cache)
    elif activation == "relu":
        dZ = relu_backward(dA, activation_cache)
        dA_prev, dW, db = linear_backward(dZ, linear_cache)

    return dA_prev, dW, db


def L_model_backward(AL, Y, caches):
    grads = {}
    L = len(caches)
    m = AL.shape[1]
    Y = Y.reshape(AL.shape)

    # L = -YlogA - (1-Y)log(1-A)
    dAL = -(np.divide(Y, AL) - np.divide(1 - Y, 1 - AL))

    current_cache = caches[L-1]
    grads["dA"+str(L)], grads["dW"+str(L)], grads["db"+str(L)] = linear_activation_backward(dAL, current_cache, activation="sigmoid")

    for l in reversed(range(L-1)):
        current_cache = caches[l]
        
        dA_prev_temp, dW_temp, db_temp = linear_activation_backward(grads["dA"+str(l+2)], current_cache, activation="relu")

        grads["dA"+str(l+1)] = dA_prev_temp
        grads["dW"+str(l+1)] = dW_temp
        grads["db"+str(l+1)] = db_temp

    return grads

