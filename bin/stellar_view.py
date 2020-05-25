"""
CLI utility to view stellar logs (maps).
"""
import sys
import argparse
import numpy as np
import matplotlib.pyplot as plt

from bresenham import bresenham

from stellar.cognition import mapping
from stellar.cognition.planning import GridPlaner
from stellar.models.robot import Robot


def connect_pylons(positions, occupancy_grid_map):
    for index, position in enumerate(positions):
        next_index = (index + 1) % len(positions)
        next_element = positions[next_index]

        x1 = int(position[0])
        y1 = int(position[1])
        x2 = int(next_element[0])
        y2 = int(next_element[1])
        for x, y in bresenham(x1, y1, x2, y2):
            occupancy_grid_map[y, x] = mapping.LOG_ODD_MAX
            occupancy_grid_map[y+1, x] = mapping.LOG_ODD_MAX
            occupancy_grid_map[y, x+1] = mapping.LOG_ODD_MAX

    return occupancy_grid_map


def dist(a, b):
    """Euclidian Distance between two points"""
    x1, y1 = a
    x2, y2 = b
    return np.sqrt(np.square(x2-x1) + np.square(y2-y1))


def main(mapfile):

    # Prepare environment from saved parcours
    occupancy_grid_map = np.load(mapfile)
    pylons = [
        (50, 75),
        (75, 150),
        (150, 150),
        (100, 75),
        (60, 50)
    ]

    occupancy_grid_map = connect_pylons(pylons, occupancy_grid_map)

    planner = GridPlaner()

    # Sample waypoints to direct A*
    robot_history = [
        (40, 100),
        (40, 150),
        (100, 170),
        (170, 170),
        (160, 130),
        (145, 100),
        (130, 70),
        (60, 30),
        (25, 25),
    ]

    should_plot_waypoints = False
    [plt.plot(x, y, marker='x')
     for x, y in robot_history if should_plot_waypoints]

    path = list()
    to_ = None
    from_ = (25, 25)
    for waypoint in robot_history:
        to_ = waypoint
        print(from_, "=>", to_)
        planned_path = planner.plan(occupancy_grid_map, from_, to_)
        path.extend(planned_path)
        from_ = waypoint

    # path = planner.plan(occupancy_grid_map, (25, 25), robot_history[0])
    # path_second = planner.plan(occupancy_grid_map, path[-1], robot_history[1])
    # path.extend(path_second)
    path = planner.smoothen(occupancy_grid_map, path)
    path_arr = np.array(path)
    plt.plot(path_arr[:, 0], path_arr[:, 1], 'y')

    plt.imshow(occupancy_grid_map, origin='lower', cmap='gray')
    #plt.plot(25, 25, marker='o')
    plt.show(block=True)

    return

    # Robot
    robot = Robot()
    robot.set(80, 180, 0)

    # print(robot.x)

    params, err = twiddle(path, len(path))
    # print(params)

    print(params, err)
    tau_p = 0.001
    tau_d = 3
    tau_i = 0.0004
    tau_p, tau_d, tau_i = params
    xt, yt, _ = run(robot, path, tau_p, tau_d, tau_i, n=len(path))
    for x, y in zip(xt, yt):
        plt.plot(x, y, marker='o')

    print(cte(robot, path, -1))

    print("Robot", str(robot), "\t=>", path[249])

    plt.imshow(occupancy_grid_map, origin='lower', cmap='gray')
    #plt.plot(25, 25, marker='o')
    plt.show(block=True)


def cte(robot, reference, t):
    reference_point = reference[t]

    # return robot.y
    return abs(dist(reference_point, (robot.x, robot.y)))
    if robot.x < reference_point[0]:
        return d
    else:
        return -d


def run(robot, reference, tau_p, tau_d, tau_i, n=100, speed=1.0):
    """Run the robot simulation."""
    x_trajectory = []
    y_trajectory = []

    previous_crosstrack_error = cte(robot, reference, 0)
    integral_cte = 0.0
    steer = robot.theta
    err = 0
    for t in range(n):
        if t < 200:
            continue
        crosstrack_error = cte(robot, reference, t)
        differential_cte = (crosstrack_error - previous_crosstrack_error)
        previous_crosstrack_error = crosstrack_error
        integral_cte += crosstrack_error

        steer = (-tau_p * crosstrack_error - tau_d *
                 differential_cte)

        steer = np.radians(steer)
        #print("=>", steer)
        # print(steer)
        robot = robot.move(speed, steer)
        err += crosstrack_error

        x_trajectory.append(robot.x)
        y_trajectory.append(robot.y)

    return x_trajectory, y_trajectory, err / n


def twiddle(path, n, tol=0.01):
    # TODO: Add code here
    # Don't forget to call `make_robot` before you call `run`!
    p = [0, 0, 0.0]
    dp = [1.0, 1.0, 1.0]
    robot = Robot()
    robot.set(60, 180, 0)
    x_trajectory, y_trajectory, best_err = run(robot, path, *p, n=n)

    it = 0
    while sum(dp) > tol:
        # print("Iteration {}, best error = {}".format(it, best_err))
        for i in range(len(p)):
            p[i] += dp[i]
            robot = Robot()
            robot.set(60, 180, 0)
            x_trajectory, y_trajectory, err = run(robot, path, *p, n=n)

            if err < best_err:
                best_err = err
                dp[i] *= 1.1
            else:
                p[i] -= 2 * dp[i]

                x_trajectory, y_trajectory, err = run(robot, path, *p, n=n)

                if err < best_err:
                    best_err = err
                    dp[i] *= 1.1
                else:
                    p[i] += dp[i]
                    dp[i] *= 0.9
        it += 1
    return p, best_err


if __name__ == "__main__":
    # parser = argparse.ArgumentParser()
    # parser.add_argument("--saved-map",
    #                     required=True,
    #                     help="Path to stored map.")
    # args = parser.parse_args()

    try:
        # main(args.saved_map)
        main("logs/ogm_savefile_533.np")
    except KeyboardInterrupt:
        sys.exit(1)
