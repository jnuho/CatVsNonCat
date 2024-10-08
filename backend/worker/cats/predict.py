import numpy as np
# import matplotlib.pyplot as plt
import requests
from PIL import Image
from io import BytesIO

from .forward import *

# plt.rcParams['figure.figsize'] = (5.0, 4.0) # set default size of plots
# plt.rcParams['image.interpolation'] = 'nearest'
# plt.rcParams['image.cmap'] = 'gray'


def predict_v2(X, parameters):
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
    # print("Accuracy: "  + str(np.sum((p == y)/m)))
        
    return p


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


def test_image_url(img_url, parameters):
    # _, _, _, _, classes = load_data()
    classes = [b'non-cat', b'cat']

    response = requests.get(img_url)
    X = Image.open(BytesIO(response.content))
    X = X.resize((64, 64))
    X = np.array(X)

    # Check the number of channels and reshape accordingly
    # RGB
    if X.size == 64 * 64 * 3:
        X = X.reshape((64*64*3, 1))
    # RGBA
    elif X.size == 64 * 64 * 4:
        X = X[:, :, :3]  # Discard the alpha channel (Transparency)
        X = X.reshape((64*64*3, 1))
    else:
        raise ValueError("Unexpected image size: {}".format(X.size))

    X = X / 255.

    """
    This function is used to predict the results of a  L-layer neural network.
    
    Arguments:
    X -- data set of examples you would like to label
    parameters -- parameters of the trained model
    
    Returns:
    p -- predictions for the given dataset X
    """
    p = predict_v2(X, parameters)

    L = len(parameters) // 2
    return str(L) + "-layer model predicts a \"" + classes[int(np.squeeze(p))].decode("utf-8") +  "\" : " + img_url.split('/')[-1]


# def test_image(img_name, my_label_y, parameters):
#     # _, _, _, _, classes = load_data()
#     classes = [b'non-cat', b'cat']

#     #DeprecationWarning: Starting with ImageIO v3 the behavior of this function will switch to that of iio.v3.imread. To keep the current behavior (and make this warning disappear) use `import imageio.v2 as imageio` or call `imageio.v2.imread` directly.
#     num_px = 64
#     ## START CODE HERE ##
#     # base_path = os.path.dirname(os.path.abspath(__file__))
#     # my_image = os.path.join(base_path, 'cats/cat_body')
#     # my_image = "cats/cat_body.jpg" # change this to the name of your image file
#     # my_image = "my_image.jpg" # change this to the name of your image file
#     my_label_y = [my_label_y] # the true class of your image (1 -> cat, 0 -> non-cat)
#     ## END CODE HERE ##

#     fname = "backend/worker/cats/images/" + img_name
#     # image = np.array(ndimage.imread(fname, flatten=False))
#     image = np.array(iio.imread(fname))
#     # my_image = scipy.misc.imresize(image, size=(num_px,num_px)).reshape((num_px*num_px*3,1))
#     my_image = resize(image, (num_px, num_px)).reshape((num_px*num_px*3,1))
#     # my_image = scipy.misc.imresize(image, size=(num_px,num_px)).reshape((num_px*num_px*3,1))
#     my_image = my_image/255.

#     my_predicted_image = predict(my_image, my_label_y, parameters)

#     # plt.imshow(img_name)
#     print ("y = " + str(np.squeeze(my_predicted_image)) + ", your L-layer model predicts a \"" + classes[int(np.squeeze(my_predicted_image)),].decode("utf-8") +  "\" picture: " + img_name)



# WITHOUT TRAINING AGAIN, JUST LOAD .pyc
# Load parameters using np.load with allow_pickle=True
# data = np.load('parameters.npz', allow_pickle=True)
# parameters = {key: data[key].item() for key in data}["parameters"]

# train_x_orig, train_y, test_x_orig, test_y, classes = load_data()

# train_x_flatten = train_x_orig.reshape(train_x_orig.shape[0], -1).T
# train_x = train_x_flatten / 255
# test_x_flatten = test_x_orig.reshape(test_x_orig.shape[0], -1).T
# test_x = test_x_flatten / 255

# pred_train = predict(train_x, train_y, parameters)
# pred_test = predict(test_x, test_y, parameters)

# print("Train predictions: " + str(pred_train))
# print("Test predictions: " + str(pred_test))


### Example of a picture ###
# train_x_orig, train_y_orig, test_x_orig, test_y_orig, classes = load_data()

# Standardize data to have feature values between 0 and 1.
# index = 16
# plt.imshow(test_x_orig[index])
# print ("y = " + str(test_y_orig[0,index]) + ". It's a " + classes[test_y_orig[0,index]].decode("utf-8") +  " picture.")
# my_predicted_image = predict(test_x[:,index].reshape(12288,1), [test_y_orig[0,index]], parameters)
# print ("y = " + str(np.squeeze(my_predicted_image)) + ", your L-layer model predicts a \"" + classes[int(np.squeeze(my_predicted_image)),].decode("utf-8") +  "\" picture.")

# test_image("cat_body.jpg", 1, parameters)
# test_image("white_cat.jpg", 1, parameters)
# test_image("weird_cat.jpg", 1, parameters)
# test_image("gargouille.jpg", 0, parameters)
# test_image("test/cat/00000001_000.jpg", 1, parameters)
# test_image("test/noncat/horse-60.jpg", 0, parameters)
# test_image("train/cat/cat.99.jpg", 1, parameters)
# print(test_image_url("https://cdn.pixabay.com/photo/2024/01/29/20/40/cat-8540772_1280.jpg", parameters))
# print(test_image_url("https://cdn.pixabay.com/photo/2024/02/17/00/18/cat-8578562_1280.jpg", parameters))
# print(test_image_url("https://cdn.pixabay.com/photo/2023/06/29/10/33/lion-8096155_1280.png",parameters))
# print(test_image_url("https://cdn.pixabay.com/photo/2016/03/27/21/52/woman-1284411_1280.jpg", parameters))



