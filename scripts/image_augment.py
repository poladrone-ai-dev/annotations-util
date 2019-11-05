# This Python 3 environment comes with many helpful analytics libraries installed
# It is defined by the kaggle/python docker image: https://github.com/kaggle/docker-python
# For example, here's several helpful packages to load in

import numpy as np  # linear algebra
# import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)

# Input data files are available in the "../input/" directory.
# For example, running this (by clicking run or pressing Shift+Enter) will list the files in the input directory

import os
# print(os.listdir(r"C:\Users\Brian Sia\Desktop\image-augmentation\input"))

# Any results you write to the current directory are saved as output.

'''
Image Augmentation is the common used technique to improve the performance of computer vision system.
Refer to the W2 of Convolutional Neutral Network Course on Cousera.
specially in the WIDS dataset, which is an unbalanced dataset.
Upsampling the images with oil-palm is the way to handle the unbalanced problem.
Image augmentation artificially creates training images through different ways of processing or combination of multiple processing,
such as mirroring, random rotation, shifts, shear and flips, etc.
Keras has keras.preprocessing.image.ImageDataGenerator function to do image augmentation. Here showed how to use OpenCV to rotate, flip, and add Gaussian noise to original images.

Reference:
https://towardsdatascience.com/image-augmentation-examples-in-python-d552c26f2873
https://medium.com/@thimblot/data-augmentation-boost-your-image-dataset-with-few-lines-of-python-155c2dc1baec

'''

import cv2
import random

class Data_augmentation:
    def __init__(self, path, image_name):
        '''
        Import image
        :param path: Path to the image
        :param image_name: image name
        '''
        self.path = path
        self.name = image_name
        print(path + image_name)
        self.image = cv2.imread(path + image_name)

    def rotate(self, image, angle=90, scale=1.0):
        '''
        Rotate the image
        :param image: image to be processed
        :param angle: Rotation angle in degrees. Positive values mean counter-clockwise rotation (the coordinate origin is assumed to be the top-left corner).
        :param scale: Isotropic scale factor.
        '''
        w = image.shape[1]
        h = image.shape[0]
        # rotate matrix
        M = cv2.getRotationMatrix2D((w / 2, h / 2), angle, scale)
        # rotate
        image = cv2.warpAffine(image, M, (w, h))
        return image

    def flip(self, image, vflip=False, hflip=False):
        '''
        Flip the image
        :param image: image to be processed
        :param vflip: whether to flip the image vertically
        :param hflip: whether to flip the image horizontally
        '''
        if hflip or vflip:
            if hflip and vflip:
                c = -1
            else:
                c = 0 if vflip else 1
            image = cv2.flip(image, flipCode=c)
        return image

    def AddNoise(self, noise_type, image):

        if noise_type == "gauss":
            row, col, ch = image.shape
            mean = 0
            var = 0.1
            sigma = var ** 0.5
            gauss = np.random.normal(mean, sigma, (row, col, ch))
            gauss = gauss.reshape(row, col, ch)
            noisy = image + gauss
            return noisy

        elif noise_type == "s&p":
            row, col, ch = image.shape
            s_vs_p = 0.5
            amount = 0.004
            out = np.copy(image)
            # Salt mode
            num_salt = np.ceil(amount * image.size * s_vs_p)
            coords = [np.random.randint(0, i - 1, int(num_salt))
                      for i in image.shape]
            out[coords] = 1

            # Pepper mode
            num_pepper = np.ceil(amount * image.size * (1. - s_vs_p))
            coords = [np.random.randint(0, i - 1, int(num_pepper))
                      for i in image.shape]
            out[coords] = 0
            return out

        elif noise_type == "poisson":
            vals = len(np.unique(image))
            vals = 2 ** np.ceil(np.log2(vals))
            noisy = np.random.poisson(image * vals) / float(vals)
            return noisy

        elif noise_type == "speckle":
            row, col, ch = image.shape
            gauss = np.random.randn(row, col, ch)
            gauss = gauss.reshape(row, col, ch)
            noisy = image + image * gauss
            return noisy

    def image_augment(self, save_path):
        '''
        Create the new image with imge augmentation
        :param path: the path to store the new image
        '''
        img = self.image.copy()
        v_flip = self.flip(img, vflip=True, hflip=False)
        h_flip = self.flip(img, vflip=False, hflip=True)
        # img_rot = self.rotate(img)
        # img_gaussian = self.AddNoise('gauss', img)

        name_int = self.name[:len(self.name) - 4]
        cv2.imwrite(save_path + '%s' % str(name_int) + '-f0.jpg', v_flip)
        cv2.imwrite(save_path + '%s' % str(name_int) + '-f1.jpg', h_flip)
        # cv2.imwrite(save_path + '%s' % str(name_int) + '_rot.jpg', img_rot)
        # cv2.imwrite(save_path + '%s' % str(name_int) + '_GaussianNoise.jpg', img_gaussian)


def main():
    file_dir = r"D:\training_data\20_context\images\\"
    output_path = r"D:\training_data\20_context\images_aug\\"

    for root, _, files in os.walk(file_dir):
        print(root)
    for file in files:
        raw_image = Data_augmentation(root, file)
        raw_image.image_augment(output_path)

main()