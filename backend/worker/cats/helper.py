import os
from PIL import Image

from worker.cats.load_data import *


def resize_image():
    # Use the function to resize your image
    image_dirs = ["images/test/cat",
                  "images/test/noncat",
                  "images/train/cat",
                  "images/train/noncat"]
    # Get a list of all files in the directory

    for image_dir in image_dirs:
        image_files = os.listdir(image_dir)

        # Filter the list for files ending with '.jpg' and starting with '0000000'
        image_files = [f for f in image_files if f.endswith('.jpg')]

        # Iterate over the image files
        for image_file in image_files:
            # Full path to the image file
            fname = os.path.join(image_dir, image_file)
            input_image_path = fname
            output_image_path = fname

            size = (64, 64)

            original_image = Image.open(input_image_path)
            width, height = original_image.size
            print(f"The original image size is {width} wide x {height} tall")

            resized_image = original_image.resize(size)
            width, height = resized_image.size
            print(f"The resized image size is {width} wide x {height} tall")
            # resized_image.show()

            # Save the resized image to the output path
            resized_image.save(output_image_path)


def preprocess_images(x):
    mean = x.mean(axis=0)
    std_dev = x.std(axis=0)
    x = (x - mean) / std_dev
    return x

