"""
Stellar CLI.

Currently used for demo and experimenting purposes.
"""
import argparse
import sys
from time import time
from enum import Enum

import numpy as np
from roboviz import MapVisualizer
from skimage.transform import resize
from bresenham import bresenham

from stellar.action import motion
from stellar.cognition import mapping
from stellar.models.astar import AStarPlanner
from stellar.models.gridmap import OccupancyGridMap
from stellar.models.robot import Robot
from stellar.perception import sensors
from stellar.perception.sensors import SensorArray
from stellar.simulation.data import load_world, png_to_ogm

VERSION = "0.0.1"
HEADER = r"""
       _____ _______ ______ _      _               _____
      / ____|__   __|  ____| |    | |        /\   |  __ \
     | (___    | |  | |__  | |    | |       /  \  | |__) |
      \___ \   | |  |  __| | |    | |      / /\ \ |  _  /
      ____) |  | |  | |____| |____| |____ / ____ \| | \ \
     |_____/   |_|  |______|______|______/_/    \_\_|  \_\

     v%s
""" % VERSION
print(65*'=', end='')
print(HEADER, end='')
print(65*'=')


# World parameters
MAP_SIZE_PIXELS = 200
MAP_SIZE_METERS = 20
SPEED_MPS = 0.5


class MODE(Enum):
    WALL_FOLLOW = 1


def main(parcours_filename):

    # Create a MapVisualizer to track the robots behaviour
    viz = MapVisualizer(MAP_SIZE_PIXELS, MAP_SIZE_METERS,
                        'StellarAI Visualization', True)

    # Load preconstructed environment / world
    mapbytes = np.array(png_to_ogm(parcours_filename, normalized=True))

    mapbytes = resize(mapbytes, (MAP_SIZE_PIXELS, MAP_SIZE_PIXELS))
    occupancy_grid_map = np.zeros(mapbytes.shape)

    # Sonar configuration: three sensors are mounted on the roboter
    # each facing a different direction: left, ahead and right. Further,
    # each sonar sensor has an opening angle of 15 degress.
    #
    # Maximum capacity is set to 8 meters.
    z_max = int(4 / viz.map_scale_meters_per_pixel)
    sonar_opening_angle = np.deg2rad(15)
    sensors = SensorArray(z_max)

    # Three sonar sensors are mounted on the robot, each facing another
    # direction, with their respective relative angles to the robots
    # driving direction (-90°, 0°, +90°)
    # sonar_bearing_angles = np.array([(1/2)*np.pi, 0, -(1/2)*np.pi])
    # TODO: sonar_bearing_angles = np.array([np.deg2rad(-90), 0, np.deg2rad(90)])

    # Initialize our robot with an initial pose
    robot = Robot()
    robot.set(2, 2, 90)

    # Record the history of the robot
    robot_history = list()

    # Start timing
    prevtime = time()

    change_direction = 0

    mode = MODE.WALL_FOLLOW

    # Enter main loop
    step = 0
    print("=> Driving in Mode: ", mode.name)

    pylons = [
        (5.0, 7.5),
        (7.5, 15.0),
        (15.0, 15.0),
        (12.5, 10.0),
        (10.0, 6.0)
    ]

    while True:
        step += 1

        occupancy_grid_map = connect_pylons(
            pylons, occupancy_grid_map, viz.map_scale_meters_per_pixel)
        if not viz.display(robot, occupancy_grid_map, mapping.LOG_ODD_MIN, mapping.LOG_ODD_MAX):
            with open(f"logs/ogm_savefile_{step}.np", 'wb+') as fd:
                np.save(fd, occupancy_grid_map)
            exit(0)

        currtime = time()
        s = SPEED_MPS * (currtime - prevtime)
        prevtime = currtime

        # Set new pose
        if change_direction:
            new_direction = robot.theta + change_direction
        else:
            new_direction = robot.theta

        robot = robot.move(s, new_direction)

        # Display the pylons
        [viz.show_pylon((x, y)) for x, y in pylons]
        # Capture distance measurements from sonar sensors

        # Get current position in grid (pixel/cell wise)
        map_pose = robot.pose_in_grid(viz.map_scale_meters_per_pixel)
        distance_measurements = sensors.sense(mapbytes, map_pose)

        # Update occupancy grid map with new information
        for angle, measurement in distance_measurements:
            occupancy_grid_map = mapping.update_occupancy_map(
                occupancy_grid_map,
                map_pose,
                measurement,
                angle,
                sonar_opening_angle,
                z_max
            )

        # Update robots pose
        if mode == MODE.WALL_FOLLOW:
            front, left, right = [distance * viz.map_scale_meters_per_pixel
                                  for _, distance in distance_measurements]
            change_direction = follow_wall(front, left, right)

    # Postprocessing


def connect_pylons(positions, occupancy_grid_map, scale):
    for index, position in enumerate(positions):
        next_index = (index + 1) % len(positions)
        next_element = positions[next_index]

        x1 = int(position[0] / scale)
        y1 = int(position[1] / scale)
        x2 = int(next_element[0] / scale)
        y2 = int(next_element[1] / scale)
        for x, y in bresenham(x1, y1, x2, y2):
            occupancy_grid_map[y, x] = mapping.LOG_ODD_MAX

    return occupancy_grid_map


def follow_wall(front, left, right):
    """Simple wall follower procedure.

    Returns:
        Change in direction.

    """
    change_direction = 0

    F = (0 < front < 4)
    L = (0 < left < 4)
    R = (0 < right < 4)

    print("=> front", front)
    print("=> left", left)
    print("=> right", right)
    print("-----")

    if 0 < front < 3:
        change_direction = -10
    elif 1.0 <= left <= 2.0:
        # we're good
        change_direction = 0
    elif 0 < left < 1.0:
        change_direction = -10
    elif left > 2.0:
        change_direction = 10

    return change_direction

    # elif (F and L):
    #    change_direction = -30

    # robot_history.append(robot)

    # TODO
    # distance_measurements = [sensors.sense_distance(world, pose, angle, z_max=z_max)
    #                          for angle in sonar_bearing_angles]

    # for i, distance in enumerate(distance_measurements):
    #     if distance == -1 or distance > z_max:
    #         continue

    #     occupancy_map = update_occupancy_map(
    #         occupancy_map, pose, distance, sonar_bearing_angles[i], sonar_opening_angle, z_max)

    # occupancy_map = np.clip(
    #     occupancy_map, a_max=LOG_ODD_MAX / 10, a_min=LOG_ODD_MIN / 10)

    # 3D Plot
    # data = occupancy_map
    # X, Y = np.meshgrid(x, y)
    # fig = plt.figure()
    # ax = fig.add_subplot(111, projection='3d')
    # ax.plot_surface(X, Y, data, rstride=1, cstride=1)
    # plt.show(block=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--parcours",
                        help="Path to parcours image.")
    args = parser.parse_args()

    try:
        main(args.parcours)
    except KeyboardInterrupt:
        sys.exit(1)
