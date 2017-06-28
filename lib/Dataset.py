#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: hg3n
"""

from scipy import misc
from skimage import io
from os import listdir, path


class Dataset:
    def __init__(self, data_path, target, size_exponent):
        """
        c'tor
        :param file:
        :param target:
        :param size_exponent:
        """
        self.data_path = data_path
        self.target = target
        self.size_exponent = size_exponent
        self.images = None
        self.targets = None

    def load(self):
        """
        load single dataset and store in obj
        :return:
        """

        # get files in folder
        files = [f for f in listdir(self.data_path)]
        print("loading images from folder: %s" % self.data_path)

        images = []
        image_targets = []
        for f in files:
            filepath = path.join(self.data_path, f)
            images.append(io.imread(filepath, as_grey=True))
            image_targets.append(self.target)

        # define new size and resize images
        new_size = (2 ** self.size_exponent, 2 ** self.size_exponent)
        for i in range(0, len(images)):
            # images[i] = transform.resize(images[i], new_size)
            images[i] = misc.imresize(images[i], new_size) / 16

        self.images = images
        self.targets = image_targets

    def __str__(self):
        """
        overloaded print function
        :return:
        """
        return "<Dataset | file: " + self.data_path + " | " + self.target + ">"
