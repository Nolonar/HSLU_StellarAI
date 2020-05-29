import numpy as np
from math import floor, ceil

from bresenham import bresenham


class SensorArray:
    """An array of sensors."""

    sonar_sensors = [
        ('front',   np.radians(0)),
        ('outter',  np.radians(90)),
        ('inner',   np.radians(-90))
    ]

    def __init__(self, z_max):
        """Initialize a new sensor array.

        Args:
            z_max: Maximum distance for the sonar sensors.

        """
        self.z_max = z_max
        self.sonar_opening_angle = np.radians(15)

    def sense(self, world, map_pose):
        """Returns current sensor measurements about the world."""
        measurements = list()
        for _, sonar_angle in self.sonar_sensors:
            distance = sense_distance(
                world, map_pose, sonar_angle, z_max=self.z_max)
            measurements.append((sonar_angle, distance))

        return measurements


def get_occupied_cell_from_distance(world, pose, distance, angle):
    xr, yr, theta = pose
    angle = theta + angle

    xo = distance * np.cos(angle) + xr
    yo = distance * np.sin(angle) + yr

    return (xo, yo)


def sense_distance(world, position, direction, threshold=0.5, z_max=10):
    """
    Returns distance to nearest obstacle in given direction.

    Args:
        world:      Gridmap representing the world.
        position:   Current robots pose.
        direction:  Direction that the sensor is facing.

    Returns:
        Distance to nearest obstacle in given direction or -1 if
        there was any error.
    """
    xr, yr, theta = position
    angle = theta + direction

    x_max = floor(z_max * np.cos(angle) + xr)
    y_max = floor(z_max * np.sin(angle) + yr)

    # Span bresenham line continually to z_max with given sonar angle.
    # When the first obstacle is detected, break and return the sensed
    # (x, y) coordinates of the object, where the ping reflected.

    # TODO: Check boundaries
    ping_reflected_at_xy = (0, 0)
    for x2, y2 in bresenham(xr, yr, x_max, y_max):
        if world[y2, x2] > threshold:
            ping_reflected_at_xy = (x2, y2)
            break

    if ping_reflected_at_xy == (0, 0):
        return -1
    else:
        x2, y2 = ping_reflected_at_xy
        return np.sqrt((xr - x2)**2 + (yr - y2)**2)


def approximate_obstacle_position(world, position, direction, z):
    """Given a sensor measurement `z`, returns the approximate global
    position of the sensed obstacle.

    Args:
        world:      Gridmap representing the world.
        position:   Robots current pose (x, y, theta).
        direction:  Direction that the sensor is facing.
        z:          Sensor measurement.
    """
    x, y, theta = position
    # distance = sense_distance(world, position, direction, threshold=threshold)
    distance = z
    if distance == -1:
        return (-1, -1)

    # TODO(1) swap values
    directions = {
        '>': (y, x + distance),
        'v': (distance + y, x),
        '^': (y - distance, x),
        '<': (y, x - distance)
    }

    return directions[direction]
