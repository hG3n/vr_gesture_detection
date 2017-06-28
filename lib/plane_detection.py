import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

import scipy.optimize
import functools
from numpy.linalg import norm


def main():
    content = load_file("../old_gpls/gesture_2.gpl")
    print(content)
    mat = []
    for line in content:
        foo = line.split(" ")

        for i in range(len(foo)):
            foo[i] = float(foo[i])
        mat.append(foo)

    # create numpy array
    points = np.asarray(mat)

    # plot fuck
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(points[:, 0], points[:, 1], points[:, 2], alpha=0.1, color=[0, 0, 1])

    #### THIS IS THE FUNCTION U NEED TO USE EPHRA MIMIMI
    p_points = project_3d_points_to_2d_space(points)

    # plot fuck
    ax.set_xlim(0.7, 0.9), ax.set_ylim(0, 0.4), ax.set_zlim(0.9, 1.1)
    ax.plot_surface(xx, yy, z, alpha=0.2, color=[0, 1, 0])

    # plot fuck
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.scatter(p_points[:, 0], p_points[:, 1])

    # show all figures
    plt.show()


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

    # for all points in the list
    p_points = []
    for p in points:
        proj = p - np.dot(p, normal) * normal

        x_axis = np.array([1, 0, 0])
        x_axis = x_axis - np.dot(x_axis, normal) * normal
        y_axis = np.cross(normal, x_axis)

        x_val = np.dot(proj, x_axis)
        y_val = np.dot(proj, y_axis)

        p_points.append([x_val, y_val])

    return np.asarray(p_points)


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


def load_file(file_name):
    result = [line.rstrip('\n') for line in open(file_name)]
    return result


if __name__ == '__main__':
    main()
