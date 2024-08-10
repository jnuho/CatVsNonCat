import numpy as np
# import matplotlib.pyplot as plt
import os
# from PIL import Image

from .load_data import *
from .init_params import *
from .forward import *
from .compute_cost import *
from .backward import *
from .update_params import *




# plt.rcParams['figure.figsize'] = (5.0, 4.0) # set default size of plots
# plt.rcParams['image.interpolation'] = 'nearest'
# plt.rcParams['image.cmap'] = 'gray'



# def resize_image():
#     # Use the function to resize your image
#     image_dirs = ["images/test/cat",
#                   "images/test/noncat",
#                   "images/train/cat",
#                   "images/train/noncat"]
#     # Get a list of all files in the directory

#     for image_dir in image_dirs:
#         image_files = os.listdir(image_dir)

#         # Filter the list for files ending with '.jpg' and starting with '0000000'
#         image_files = [f for f in image_files if f.endswith('.jpg')]

#         # Iterate over the image files
#         for image_file in image_files:
#             # Full path to the image file
#             fname = os.path.join(image_dir, image_file)
#             input_image_path = fname
#             output_image_path = fname

#             size = (64, 64)

#             original_image = Image.open(input_image_path)
#             width, height = original_image.size
#             print(f"The original image size is {width} wide x {height} tall")

#             resized_image = original_image.resize(size)
#             width, height = resized_image.size
#             print(f"The resized image size is {width} wide x {height} tall")
#             # resized_image.show()

#             # Save the resized image to the output path
#             resized_image.save(output_image_path)


# def preprocess_images(x):
#     mean = x.mean(axis=0)
#     std_dev = x.std(axis=0)
#     x = (x - mean) / std_dev
#     return x

def L_layer_model(X, Y, layers_dims, learning_rate = 0.0075, num_iterations = 3000, print_cost=False):
    #lr was 0.009
    """
    Implements a L-layer neural network: [LINEAR->RELU]*(L-1)->LINEAR->SIGMOID.
    
    Arguments:
    X -- data, numpy array of shape (number of examples, num_px * num_px * 3)
    Y -- true "label" vector (containing 0 if cat, 1 if non-cat), of shape (1, number of examples)
    layers_dims -- list containing the input size and each layer size, of length (number of layers + 1).
    learning_rate -- learning rate of the gradient descent update rule
    num_iterations -- number of iterations of the optimization loop
    print_cost -- if True, it prints the cost every 100 steps
    
    Returns:
    parameters -- parameters learnt by the model. They can then be used to predict.
    """

    # np.random.seed(1)
    costs = []                         # keep track of cost
    
    # Parameters initialization. (≈ 1 line of code)
    ### START CODE HERE ###
    parameters = initialize_parameters_deep(layers_dims)
    ### END CODE HERE ###
    
    # Loop (gradient descent)
    for i in range(0, num_iterations):

        # Forward propagation: [LINEAR -> RELU]*(L-1) -> LINEAR -> SIGMOID.
        ### START CODE HERE ### (≈ 1 line of code)
        AL, caches = L_model_forward(X, parameters)
        ### END CODE HERE ###
        
        # Compute cost.
        ### START CODE HERE ### (≈ 1 line of code)
        cost = compute_cost(AL, Y)
        ### END CODE HERE ###
    
        # Backward propagation.
        ### START CODE HERE ### (≈ 1 line of code)
        grads = L_model_backward(AL, Y, caches)
        ### END CODE HERE ###
 
        # Update parameters.
        ### START CODE HERE ### (≈ 1 line of code)
        parameters = update_parameters(parameters, grads, learning_rate)
        ### END CODE HERE ###
                
        # Print the cost every 100 training example
        if print_cost and i % 100 == 0:
            print ("Cost after iteration %i: %f" %(i, cost))
        if print_cost and i % 100 == 0:
            costs.append(cost)
    # plot the cost
    # plt.plot(np.squeeze(costs))
    # plt.ylabel('cost')
    # plt.xlabel('iterations (per tens)')
    # plt.title("Learning rate =" + str(learning_rate))
    # plt.show()

    return parameters


# train_x, train_y = load_train_x_and_y()
# test_x, test_y = load_test_x_and_y()
# train_x = preprocess_images(train_x)
# test_x = preprocess_images(test_x)

# print(train_x.shape)
# print(train_y.shape)
# print(test_x.shape)
# print(test_y.shape)

# train_x_orig, train_y, test_x_orig, test_y, classes = load_data()

# train_x_flatten = train_x_orig.reshape(train_x_orig.shape[0], -1).T
# train_x = train_x_flatten / 255

# # L = 4 excluding the input feature X in layer [0]
# # [12288, 20, 7, 5, 1]
# layers_dims = [train_x.shape[0], 20, 7, 5, 1]
# parameters = L_layer_model(train_x, train_y, layers_dims, learning_rate=.0075, num_iterations=3000, print_cost=True)

# np.savez('parameters.npz', parameters=parameters)

