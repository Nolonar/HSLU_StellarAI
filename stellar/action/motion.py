import numpy as np
from math import ceil


def move(pose, number_of_steps, direction):
    """Move the robot in the world.

    Args:
        pose:           Robots current pose (x, y, theta)
        number_of_steps:    Number of steps (i.e. cells) to move.
        direction:          Direction of movement

    Returns:
        The new pose of the robot.
    """

    x_r, y_r, theta_r = pose

    theta_r += direction

    x_new = ceil(number_of_steps * np.cos(theta_r)) + x_r
    y_new = ceil(number_of_steps * np.sin(theta_r)) + y_r

    return (x_new, y_new, theta_r)
