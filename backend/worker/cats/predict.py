import numpy as np

from .helper import *
from .load_data import *
from .init_params import *
from .forward import *
from .compute_cost import *
from .backward import *
from .update_params import *


def predict(X, y, parameters):
    """
    This function is used to predict the results of a  L-layer neural network.
    
    Arguments:
    X -- data set of examples you would like to label
    parameters -- parameters of the trained model
    
    Returns:
    p -- predictions for the given dataset X
    """
    
    m = X.shape[1]
    n = len(parameters) // 2 # number of layers in the neural network
    p = np.zeros((1,m))
    
    # Forward propagation
    probas, caches = L_model_forward(X, parameters)
    # print(probas)
    
    # convert probas to 0/1 predictions
    for i in range(0, probas.shape[1]):
        if probas[0,i] > 0.5:
            p[0,i] = 1
        else:
            p[0,i] = 0
    
    #print results
    # print ("predictions: " + str(p))
    # print ("true labels: " + str(y)
    print("Accuracy: "  + str(np.sum((p == y)/m)))
        
    return p


def test_image(my_image, my_label_y):
    _, _, _, _, classes = load_data()

    #DeprecationWarning: Starting with ImageIO v3 the behavior of this function will switch to that of iio.v3.imread. To keep the current behavior (and make this warning disappear) use `import imageio.v2 as imageio` or call `imageio.v2.imread` directly.
    num_px = 64
    ## START CODE HERE ##
    # base_path = os.path.dirname(os.path.abspath(__file__))
    # my_image = os.path.join(base_path, 'cats/cat_body')
    # my_image = "cats/cat_body.jpg" # change this to the name of your image file
    # my_image = "my_image.jpg" # change this to the name of your image file
    my_label_y = [my_label_y] # the true class of your image (1 -> cat, 0 -> non-cat)
    ## END CODE HERE ##

    fname = "images/" + my_image
    # fname = "images/" + "weird_cat.jpg"
    # image = np.array(ndimage.imread(fname, flatten=False))
    image = np.array(iio.imread(fname))
    # my_image = scipy.misc.imresize(image, size=(num_px,num_px)).reshape((num_px*num_px*3,1))
    my_image = resize(image, (num_px, num_px)).reshape((num_px*num_px*3,1))
    # my_image = scipy.misc.imresize(image, size=(num_px,num_px)).reshape((num_px*num_px*3,1))
    my_image = my_image/255.

    my_predicted_image = predict(my_image, my_label_y, parameters)

    plt.imshow(image)
    print ("y = " + str(np.squeeze(my_predicted_image)) + ", your L-layer model predicts a \"" + classes[int(np.squeeze(my_predicted_image)),].decode("utf-8") +  "\" picture.")


# train_x, train_y = load_train_x_and_y()
# test_x, test_y = load_test_x_and_y()

# train_x = preprocess_images(train_x)
# test_x = preprocess_images(test_x)

# print(train_x.shape)
# print(train_y.shape)

# print(test_x.shape)
# print(test_y.shape)


# L = 4 excluding the input feature X in layer [0]
# [12288, 20, 7, 5, 1]
# np.random.seed(1)
# layers_dims = [train_x.shape[0], 20, 7, 5, 1]
# layers_dims = [train_x.shape[0], 20, 7, 1]

# train_x_orig, train_y, test_x_orig, test_y, classes = load_data()
# train_x = train_x_orig.reshape(train_x_orig.shape[0], -1).T
# train_x = train_x / 255
# test_x = test_x_orig.reshape(test_x_orig.shape[0], -1).T
# test_x = test_x / 255

# parameters = L_layer_model(train_x, train_y, layers_dims, learning_rate=.0075, num_iterations=2500, print_cost=True)

# WITHOUT TRAINING AGAIN, JUST LOAD .pyc
# parameters = load()
# pred_train = predict(train_x, train_y, parameters)
# pred_test = predict(test_x, test_y, parameters)

# Load parameters using np.load with allow_pickle=True
data = np.load('parameters.npz', allow_pickle=True)
parameters = {key: data[key].item() for key in data}
print(parameters)

train_x, train_y = load_train_x_and_y()
train_x = preprocess_images(train_x)

test_x, test_y = load_test_x_and_y()
test_x = preprocess_images(test_x)

pred_train = predict(train_x, train_y, parameters)
pred_test = predict(test_x, test_y, parameters)

print("Train predictions: " + str(pred_train))
print("Test predictions: " + str(pred_test))



### Example of a picture ###
# train_x_orig, train_y_orig, test_x_orig, test_y_orig, classes = load_data()

# Standardize data to have feature values between 0 and 1.
# index = 16
# plt.imshow(test_x_orig[index])
# print ("y = " + str(test_y_orig[0,index]) + ". It's a " + classes[test_y_orig[0,index]].decode("utf-8") +  " picture.")
# my_predicted_image = predict(test_x[:,index].reshape(12288,1), [test_y_orig[0,index]], parameters)
# print ("y = " + str(np.squeeze(my_predicted_image)) + ", your L-layer model predicts a \"" + classes[int(np.squeeze(my_predicted_image)),].decode("utf-8") +  "\" picture.")

# test_image("cat_body.jpg", 1)
# test_image("my_image.jpg", 1)
# test_image("weird_cat.jpg", 1)
# test_image("gargouille.jpg", 1)
# test_image("test/cat/00000001_000.jpg", 1)
# test_image("test/noncat/horse-60.jpg", 0)
# test_image("train/cat/cat.99.jpg", 1)


