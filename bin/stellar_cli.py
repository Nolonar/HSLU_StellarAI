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


def store_simulation_data_at_step(step, occupancy_grid_map):
    with open(f"logs/ogm_savefile_{step}.np", 'wb+') as fd:
        np.save(fd, occupancy_grid_map)


def is_in_goal(robot, goal):
    """
    Checks wether robot is in goal.
    """
    # Should robots orientation matter too?
    #goal = (0, 0, np.radians(90))
    xg, yg, tg = goal

    orientation_near_goal = (np.radians(100) <= robot.theta <= np.radians(80))
    x_position_near_goal = (xg - 1 <= robot.x <= xg + 1)
    y_position_near_goal = (yg - 1 <= robot.y <= yg + 1)
    print(robot, goal)
    return (orientation_near_goal and x_position_near_goal and y_position_near_goal)


def simulate_learning_mode(robot: Robot, world: np.ndarray, sensors: SensorArray,
                           scale: float, visualization: MapVisualizer = None):
    """
    Run the learning mode simulation.
    """
    steer = 0       # Relative change in direction
    step = 0
    occupancy_grid_map = np.zeros(world.shape)
    previous_time = time()

    goal = (robot.x, robot.y, robot.theta)
    while True:  # TODO: While not_in_goal(robot, goal)

        print("Is in goal?:", is_in_goal(robot, goal))
        if visualization is not None:
            if not visualization.display(robot, occupancy_grid_map, mapping.LOG_ODD_MIN, mapping.LOG_ODD_MAX):
                store_simulation_data_at_step(step)
                exit(0)

        # Calculate distance `s` based on MPS and timedelta
        current_time = time()
        distance_covered = SPEED_MPS * (current_time - previous_time)
        previous_time = current_time

        robot.move(distance_covered, np.radians(steer))

        # Get current position in grid (pixel/cell wise)
        map_scale_meters_per_pixel = scale  # TODO: move to map config?
        map_pose = robot.pose_in_grid(map_scale_meters_per_pixel)
        # Retrieve measurements from ultrasonic sensors
        distance_measurements = sensors.sense(world, map_pose)

        # Update occupancy grid map with new information
        for angle, measurement in distance_measurements:
            occupancy_grid_map = mapping.update_occupancy_map(
                occupancy_grid_map,
                map_pose,
                measurement,
                angle,
                sensors.sonar_opening_angle,
                sensors.z_max
            )

        # Convert sensor measurements back to meters
        front, left, right = [distance * map_scale_meters_per_pixel
                              for _, distance in distance_measurements]

        steer = motion.follow_wall(front, left, right)
        step += 1


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
    robot.set(2, 2, np.radians(90))

    # Start timing
    simulate_learning_mode(
        robot, mapbytes, sensors, viz.map_scale_meters_per_pixel, visualization=viz)

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

        # occupancy_grid_map = connect_pylons(
        #    pylons, occupancy_grid_map, viz.map_scale_meters_per_pixel)
        if not viz.display(robot, occupancy_grid_map, mapping.LOG_ODD_MIN, mapping.LOG_ODD_MAX):
            with open(f"logs/ogm_savefile_{step}.np", 'wb+') as fd:
                np.save(fd, occupancy_grid_map)
            exit(0)

        currtime = time()
        s = SPEED_MPS * (currtime - prevtime)
        prevtime = currtime

        robot.move(s, np.radians(change_direction))
        print(robot)

        # Display the pylons
        # [viz.show_pylon((x, y)) for x, y in pylons]
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
            change_direction = motion.follow_wall(front, left, right)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--parcours", required=True,
                        help="Path to parcours image.")
    args = parser.parse_args()

    try:
        main(args.parcours)
    except KeyboardInterrupt:
        sys.exit(1)
