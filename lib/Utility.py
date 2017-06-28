#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on May 10.05.17 12:02
@author: ephtron
"""

import numpy as np
from os import listdir, path
from PyQt5 import QtGui

from lib.Dataset import Dataset

import scipy.optimize
import functools


def load_datasets(directory, size_exponent):
    """
    loads datasets from directory with a given size exponent
    :param directory: specifies the directory where the samples are stored
    :param size_exponent: size to load the sample images (preferably 2**n)
    :return: list of datasets, set of targets
    """
    # get dataset folders in base dir
    basedir = [d for d in listdir(directory) if not path.isfile(d)]

    # load files
    sets = []
    targets = []
    for folder in basedir:
        # create path
        dataset_path = path.join(directory, folder)
        d = Dataset(data_path=dataset_path,
                    target=folder,
                    size_exponent=size_exponent)
        targets.append(folder)

        d.load()
        sets.append(d)

    return sets, list(set(targets))


def qimage_to_image_array(qimage):
    # using code from https://github.com/hmeine/qimage2ndarray
    from qimage2ndarray import qimage2ndarray
    # convert qimage to ndarray
    ndarray_img = qimage2ndarray.rgb_view(qimage)
    return ndarray_img


def ndarray_color_to_grey(ndarray):
    """
    creates new ndarray out of an image
    with rgb values. new ndarray has only zeros and 255s.
    :param ndarray: image_array with shape (n,n,3)
    :return: 
    """
    grey_ndarray = np.zeros((ndarray.shape[0], ndarray.shape[1]))

    # converting rgb values to black(0) and white(255)
    for r in range(ndarray.shape[0]):
        for c in range(ndarray.shape[1]):
            if np.array_equal(ndarray[r, c], [255, 255, 255]):
                grey_ndarray[r, c] = 255

    return grey_ndarray


def prepare_gpl_for_plane_detection(gpl):
    """
    read in a gpl file and create a point list out of it
    """
    mat = []
    for line in gpl:
        foo = line.split(" ")

        for i in range(len(foo)):
            foo[i] = float(foo[i])
        mat.append(foo)

    # create numpy array
    points = np.asarray(mat)

    return points

def prepare_gvl_for_plane_detection(gvl):
    """
    read in direct gesture vector list, which got created by the manipulator
    """
    mat = []
    for point_vec3 in gvl:
        point = [point_vec3[0], point_vec3[1], point_vec3[2]]
        
        mat.append(point)

    # create numpy array
    points = np.asarray(mat)

    return points


def project_3d_points_to_2d_space(point_list):
    """
    calculates the best fittin plane for a pointcloud
    using least square error and projects points to 2d
    :param point_list:
    :return:
    """

    # do fancy python shit
    fun = functools.partial(error, points=point_list)
    res = scipy.optimize.minimize(fun, [0, 0, 0])

    # abc components of plane
    a = res.x[0]
    b = res.x[1]
    c = res.x[2]

    # plane normal
    normal = np.array(np.cross([1, 0, a], [0, 1, b]))

    # some point
    point = np.array([0.0, 0.0, c])

    # d element of plane
    d = -point.dot(normal)

    # calculate z value
    xx, yy = np.meshgrid([-1, 1], [-1, 1])
    z = (-normal[0] * xx - normal[1] * yy - d) * 1. / normal[2]


    normal = np.asarray([normal]).T
    normal = create_unit_vec(normal)

    normal = np.squeeze(normal)


    # for all points in the list
    p_points = []
    for p in point_list:
        proj = p - np.dot(p, normal) * normal

        x_axis = np.array([1, 0, 0])
        x_axis = x_axis - np.dot(x_axis, normal) * normal
        y_axis = np.cross(normal, x_axis)

        x_val = np.dot(proj, x_axis)
        y_val = np.dot(proj, y_axis)

        p_points.append([x_val, y_val])

    return np.asarray(p_points)

def create_unit_vec(vec):
    print(vec)
    print(vec.shape)
    mag = np.linalg.norm(vec)
    return np.asarray([vec[0]/mag, vec[1]/mag, vec[2]/mag])

def plane(x, y, params):
    """
    calculate z value of a plane
    :param x:
    :param y:
    :param params:
    :return:
    """
    a = params[0]
    b = params[1]
    c = params[2]
    z = a * x + b * y + c
    return z


def error(params, points):
    """
    calculate the error
    :param params:
    :param points:
    :return:
    """
    result = 0
    for (x, y, z) in points:
        plane_z = plane(x, y, params)
        diff = abs(plane_z - z)
        result += diff ** 2
    return result