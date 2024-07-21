import numpy as np


def compute_cost(AL, Y):
    m = Y.shape[1]
    cost = 1/m * (-np.dot(Y, np.log(AL).T) - np.dot(1-Y, np.log(1-AL).T))

    # e.g.  [[17]] -> 17
    cost = np.squeeze(cost)

    assert(cost.shape == ())

    return cost

