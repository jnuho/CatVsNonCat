# import numpy as np
# import scipy
# from scipy import ndimage
# import os
# import imageio.v3 as iio
# from skimage.transform import resize
# from dnn_app_utils_v3 import *
# import h5py

# def load_data():
#     # Find the path to the datasets
#     dataset_path = os.path.join(os.path.dirname(__file__), 'datasets')

#     # in .venv environment
#     # train_dataset = h5py.File('datasets/train_catvnoncat.h5', "r")
#     train_dataset = h5py.File(os.path.join(dataset_path, 'train_catvnoncat.h5'), "r")
#     train_set_x_orig = np.array(train_dataset["train_set_x"][:]) # your train set features
#     train_set_y_orig = np.array(train_dataset["train_set_y"][:]) # your train set labels

#     # test_dataset = h5py.File('datasets/test_catvnoncat.h5', "r")
#     test_dataset = h5py.File(os.path.join(dataset_path, 'test_catvnoncat.h5'), "r")
#     test_set_x_orig = np.array(test_dataset["test_set_x"][:]) # your test set features
#     test_set_y_orig = np.array(test_dataset["test_set_y"][:]) # your test set labels

#     classes = np.array(test_dataset["list_classes"][:]) # the list of classes
    
#     train_set_y_orig = train_set_y_orig.reshape((1, train_set_y_orig.shape[0]))
#     test_set_y_orig = test_set_y_orig.reshape((1, test_set_y_orig.shape[0]))
    
#     return train_set_x_orig, train_set_y_orig, test_set_x_orig, test_set_y_orig, classes


# def convert_to_matrix(x, y, image_dir, num_px, my_label_y, offset):
#     # Get a list of all files in the directory
#     image_files = os.listdir(image_dir)

#     # Filter the list for files ending with '.jpg' and starting with '0000000'
#     image_files = [f for f in image_files if f.endswith('.jpg')]

#     # Iterate over the image files
#     for i, image_file in enumerate(image_files):
#         # Full path to the image file
#         fname = os.path.join(image_dir, image_file)
        
#         # Read and preprocess the image
#         image = np.array(iio.imread(fname))
#         my_image = resize(image, (num_px, num_px)).reshape((num_px*num_px*3,1))
#         my_image = my_image/255.

#         x[:, i+offset] = my_image.flatten()
#         y[:, i+offset] = my_label_y

#     return x, y


# def load_test_x_and_y():
#     """
#     return
#     'test_x' (12288, 100) where 50 is non-cat
#     'test_y' (1, 100)
#     """
#     num_px = 64

#     test_x = np.zeros((num_px * num_px * 3, 100))
#     test_y = np.zeros((1, 100))

#     test_x, test_y = convert_to_matrix(test_x, test_y, "backend/worker/cats/images/test/cat/", num_px, my_label_y=1, offset=0)
#     test_x, test_y = convert_to_matrix(test_x, test_y, "backend/worker/cats/images/test/noncat/", num_px, my_label_y=0, offset=50)

#     return test_x, test_y

# def load_train_x_and_y():
#     """
#     return
#     'train_x' (12288, 400) where 200 is non-cat
#     'train_y' (1, 400)
#     """
#     num_px = 64

#     train_x = np.zeros((num_px * num_px * 3, 400))
#     train_y = np.zeros((1, 400))

#     train_x, train_y = convert_to_matrix(train_x, train_y, "backend/worker/cats/images/train/cat/", num_px, my_label_y=1, offset=0)
#     train_x, train_y = convert_to_matrix(train_x, train_y, "backend/worker/cats/images/train/noncat/", num_px, my_label_y=0, offset=200)

#     return train_x, train_y

