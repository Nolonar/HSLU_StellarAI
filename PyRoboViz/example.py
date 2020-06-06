#!/usr/bin/env python3
'''
randomwalk.py: PyRoboViz test with random walk

Copyright (C) 2018 Simon D. Levy

This file is part of PyRoboViz.

PyRoboViz is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

PyRoboViz is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with this code.  If not, see <http:#www.gnu.org/licenses/>.
'''


from skimage.transform import resize
from stellar.simulation.data import load_world
import argparse
from time import time

import numpy as np
import png

from roboviz import MapVisualizer
from stellar.models.robot import Robot
from stellar.simulation.data import png_to_ogm
from stellar.cognition import mapping
from stellar.perception.sensors import sense_distance, get_occupied_cell_from_distance, SensorArray

MAP_SIZE_PIXELS = 200
MAP_SIZE_METERS = 20
SPEED_MPS = 0.5


def move(pose, s):
    # s = gefahrene strecke
    x, y, theta = pose
    x += s * np.cos(theta)
    y += s * np.sin(theta)
    theta += 10 * np.random.randn()
    return (x, y, theta)


def pose_in_grid(robot, scale):
    """Converts the pose to the current position in the gridmap."""
    x, y, theta = (robot.x, robot.y, robot.theta)

    xr = int(x / scale)
    yr = int(y / scale)
    theta = np.radians(theta)

    return (xr, yr, theta)


def log_distances(distances):
    s = ['[']
    for sensor_id, measurement in distances:
        s.append(f"{sensor_id} => {measurement} m\t")

    s[-1] = s[-1].rstrip('\t')
    s.append(']')
    print(''.join(s))


def log_robot(robot):
    print(f"[Robot => {robot.x}, {robot.y}, {robot.theta}]")


def log(**kwargs):
    s = []
    for k, v in kwargs.items():
        s.append(f"[{k} => {v}]")

    print('\t'.join(s))


if __name__ == '__main__':

    # Create a Visualizer object with a trajectory, centered at 0,0
    viz = MapVisualizer(MAP_SIZE_PIXELS, MAP_SIZE_METERS,
                        'StellarAI Visualization', True)

    # mapbytes = bytearray(MAP_SIZE_PIXELS * MAP_SIZE_PIXELS)
    mapbytes = np.array(png_to_ogm(
        "../data/track_second_big.png", normalized=True))

    mapbytes = resize(mapbytes, (MAP_SIZE_PIXELS, MAP_SIZE_PIXELS))

    live_update = True

    occupancy_grid_map = np.zeros(mapbytes.shape)
    # mapbytes = np.zeros((MAP_SIZE_PIXELS, MAP_SIZE_PIXELS), dtype=np.uint8)

    # Start in the center of the map with a random heading
    pose = np.array([2, 2, 90.00])

    robot = Robot()
    robot.set(pose[0], pose[1], pose[2])

    start_goal_quadrant = np.linspace(2, 4)

    # Start timing
    prevtime = time()

    history = []

    step = 0

    change_direction = 0

    # Maximum capacity
    z_max = int(8 / viz.map_scale_meters_per_pixel)
    # Configure sensors
    sensors = SensorArray(z_max)

    # Loop till user closes the display
    skip_first = 0
    while True:

        step += 1

        # Set current pose in visualizer the display, exiting gracefully if user closes it
        if not viz.display(robot, occupancy_grid_map):
            exit(0)

        currtime = time()
        s = SPEED_MPS * (currtime - prevtime)
        prevtime = currtime
        # theta = np.radians(pose[2])
        # pose[0] += s * np.cos(theta)
        # pose[1] += s * np.sin(theta)

        if change_direction:
            direction = robot.theta + change_direction
        else:
            direction = robot.theta

        robot = robot.move(s, direction)

        log_robot(robot)

        map_pose = pose_in_grid(robot, viz.map_scale_meters_per_pixel)

        distances = sensors.sense(mapbytes, map_pose)
        log_distances(distances)

        for angle, measurement in distances:
            occupancy_grid_map = mapping.update_occupancy_map(
                occupancy_grid_map,
                map_pose,
                measurement,
                angle,
                np.radians(15),
                z_max
            )

        # Collision detection
        change_direction = 0
        distance = distances[0][1]
        if distance > 0:
            target = get_occupied_cell_from_distance(
                mapbytes, map_pose, distance, 0)

            viz.show_beam(target)
            distance_m = distance * viz.map_scale_meters_per_pixel
            if distance_m < 3:
                #pose[2] -= 20
                change_direction = -20

            log(distance_m=distance_m)
