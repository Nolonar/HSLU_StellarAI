"""
Module contains path tracking related components.
"""
import numpy as np


def dist(a, b):
    """
    Euclidian Distance between two points.
    """
    x1, y1 = a
    x2, y2 = b

    return edist(a, b)

    print(np.arctan2(x2-x1, y2-y1))

    if np.arctan2(x2-x1, y2-y1) > 0:
        return edist(a, b)
    else:
        return -edist(a, b)

    # robot is left of track (outside)
    if x1 <= x2:
        return edist(a, b)

    if x1 >= x2:
        return -edist(a, b)

    # return np.sqrt(np.square(x2-x1) + np.square(y2-y1))
    # return (x2-x1) + (y2-y1)


def edist(a, b):
    """
    Euclidian Distance between two points.
    """
    x1, y1 = a
    x2, y2 = b
    return np.sqrt(np.square(x2-x1) + np.square(y2-y1))


GOO = False


def cte(robot, reference, t, plt=None):
    """
    Calculate the cross track error to reference path.
    """

    global GOO
    # Search nearest point index
    # d = [np.hypot(robot.x - icx, robot.y - icy) for icx, icy in reference]
    # d =
    # target_idx = np.argmin(d)

    # t = np.argmin([(robot.x - cx, robot.y - cy) for cx, cy in reference])
    # get nearest point out of trajectory reference list
    reference_point = get_nearest_point(robot, reference)
    print(robot.y - reference_point[1])
    if robot.x < 150 and not GOO:
        return (reference_point[0] - robot.x + robot.y - reference_point[1])
    else:
        GOO = True
    # print(reference_point, robot)
    # return (reference_point[0] - robot.x + reference_point[1] - robot.y)
    return dist((robot.x, robot.y), reference_point)


def get_nearest_point(robot, reference_trajectory):
    r = (robot.x, robot.y)
    a = [edist(k, r) for k in list(reference_trajectory)]
    i = np.argmin(a)

    p1 = reference_trajectory[i]
    p2 = reference_trajectory[i+5]

    aaa = np.arctan2(p2[1] - p1[1], p2[0] - p1[0])
    print(f"l => {aaa:.4f}, {p1}, {p2}")
    return reference_trajectory[i]
