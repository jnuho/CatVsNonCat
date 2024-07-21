import numpy as np


def initialize_parameters_deep(layers_dims):
    """
    layers_dims: L+1 layers including A^[0] = X, input feature
    """
    # np.random.seed(1)

    parameters = {}
    L = len(layers_dims)

    for l in range(1, L):
        parameters["W" + str(l)] = np.random.randn(layers_dims[l], layers_dims[l-1])/np.sqrt(layers_dims[l-1])
        parameters["b" + str(l)] = np.zeros((layers_dims[l], 1))

        assert(parameters["W" + str(l)].shape == (layers_dims[l], layers_dims[l-1]))
        assert(parameters["b" + str(l)].shape == (layers_dims[l], 1))

    return parameters