import operator
import math
import numpy as np
from enum import Enum
import scipy.misc
from skimage.draw import line, polygon_perimeter
from os import path

import matplotlib.pyplot as plt


class Point:
    instances = 0

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.id = Point.instances

        Point.instances += 1

    def __str__(self):
        return "<Point id: " + str(self.id) + " _x: " + str(self.x) + " y: " + str(self.y) + ">"

    def __lt__(self, other):
        return self.x == other.x or self.y == other.y


class ScaleMode(Enum):
    NO_SCALE = 1
    SCALE_MAX = 2


class GestureParser:
    def __init__(self, SCALE_MODE, IMAGE_DIMENSION):
        """
        c'tor
        :param SCALE_MODE:
        :param IMAGE_DIMENSION:
        """
        self.scale_mode = SCALE_MODE
        self.img_dim = IMAGE_DIMENSION

    def open_gpl_file(self, file_name):
        """
        obviously opens a file
        :param file_name: 
        :return: 
        """
        result = [line.rstrip('\n') for line in open(file_name)]
        return result

    def prepare_lines(self, lines):
        """
        do complicated line stuff
        :param lines: 
        :return: 
        """
        ret = []
        for line in lines:
            ret.append([float(x) for x in line.split(' ')])
        return ret

    def convert_gpl_to_pointlist(self, folder, file_name):
        """
        load gpl file and return list of points
        :param path: filepath
        :param file_name: name of file
        :return: 
        """
        final_path = path.join(folder, file_name)
        points = self.prepare_lines(self.open_gpl_file(final_path))
        point_list = [Point(p[0], p[1]) for p in points]
        return point_list

    def convert_point_list_to_scaled_image_array(self, point_list):
        """
        parse image from point list to numpy nd array
        :return: ndarray
        """
        # create dict containing x and y values

        #print("pointlist", point_list)
        x_dict, y_dict = {}, {}
        for p in point_list:
            # print("point ",p, "p id", p.id)
            x_dict[p.id] = p.x
            y_dict[p.id] = p.y

        # get indices of min and max x values
        min_x_idx = min(x_dict.items(), key=operator.itemgetter(1))[0]
        max_x_idx = max(x_dict.items(), key=operator.itemgetter(1))[0]

        # get min and max x values; calculate maximum distance
        min_x = x_dict[min_x_idx]
        max_x = x_dict[max_x_idx]
        max_distance_x = math.fabs(min_x) + math.fabs(max_x)

        # get indices of min and max x values
        min_y_idx = min(y_dict.items(), key=operator.itemgetter(1))[0]
        max_y_idx = max(y_dict.items(), key=operator.itemgetter(1))[0]

        # get min and max x values; calculate maximum distance
        min_y = y_dict[min_y_idx]
        max_y = y_dict[max_y_idx]
        max_distance_y = math.fabs(min_y) + math.fabs(max_y)

        # create new internet (aka image)
        image = np.zeros((self.img_dim, self.img_dim))

        p_x, p_y = 0, 0
        x_list, y_list = [], []
        for p in point_list:

            # scale the points to the maximum
            if self.scale_mode == ScaleMode.SCALE_MAX:

                p_x = int(map_to(p.x, min_x, max_x, 0, self.img_dim - 1))
                p_y = int(map_to(p.y, min_y, max_y, 0, self.img_dim - 1))
                
            # keep image dimensions and align the detected gesture to the left hand side
            elif self.scale_mode == ScaleMode.NO_SCALE:

                if max_distance_x > max_distance_y:
                    ratio = (max_distance_y * 100) / max_distance_x
                    p_x = int(map_to(p.x, min_x, max_x, 0, self.img_dim - 1))
                    p_y = int(map_to(p.y, min_y, max_y, 0, self.img_dim - 1) * ratio / 100)
                else:
                    ratio = (max_distance_x * 100) / max_distance_y
                    p_x = int(map_to(p.x, min_x, max_x, 0, self.img_dim - 1) * ratio / 100)
                    p_y = int(map_to(p.y, min_y, max_y, 0, self.img_dim - 1))

            # if the pixels are within the range save them to the list
            if (p_x < 50 and p_y < 50):
                x_list.append(p_x)
                y_list.append(p_y)

        # print("x list",x_list)
        # create polygon perimeter
        rr, cc = polygon_perimeter(y_list, x_list, (self.img_dim, self.img_dim), clip=True)

        image[rr, cc] = 255

        #print("image type", type(image))
        #print("image",image)


        # remove the connection between first and last point
        rl, cl = line(y_list[0], x_list[0], y_list[-1], x_list[-1])
        image[rl, cl] = 0

        # cast image to np array and return
        return np.asarray(image)


def save_image(array, path, file_name, file_type='jpeg'):
    """
    saves the input array to the given destination
    :param array: numpy nd array
    :param path: local path to save the image
    :param file_name: name of the file
    :param file_type: type of the file (default jpeg)
    :return:
    """
    if path[-1] != "/":
        path = path + "/"
    scipy.misc.imsave(path + file_name + '.' + file_type, array)


def map_to(value, from_min, from_max, to_min, to_max):
    """
    maps the given value from base range to new range
    :param value:
    :param from_min:
    :param from_max:
    :param to_min:
    :param to_max:
    :return:
    """
    return (value - from_min) * (to_max - to_min) / (from_max - from_min) + to_min