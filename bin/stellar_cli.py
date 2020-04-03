"""
Stellar CLI.

Currently used for demo and experimenting purposes.
"""
import numpy as np
import matplotlib.pyplot as plt

from stellar.models.gridmap import OccupancyGridMap
from stellar.models.astar import AStarPlanner

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


def detect_collision(position, grid, radius=20, threshold=0.8):
    """Simple collision detection.

    Looks in the direction of the robot (ahead, angle) to check for the
    presence of obstacles.

    Args:
        position: Tuple containing the robots current position (y, x)
        grid: Current world (OccupancyGridMap)
        radius: Detection radius
        threshold: Obstacle / grid occupancy threshold

    Returns:
        The x and y coordinates of the detected obstacles.

    """
    y, x = position

    up      = grid.world[y:y+radius, x]
    down    = grid.world[y-radius:y, x]
    right   = grid.world[y, x:x+radius]
    left    = grid.world[y, x-radius:x]

    # Return the index of the detected obstacles (i.e. occupied cell).
    return (
        np.argmax(up >= 0.8),
        np.argmax(right >= 0.8),
        np.argmax(left >= 0.8),
        np.argmax(down >= 0.8)
    )


def main():
    # Enable interactive plots
    plt.ion()

    # Robots dimensions (simple, for now)
    dim_robot = 20
    
    # start (y, x)
    start_pos = (50, 200)

    # Build gridmap (our world) from a pre-designed map
    # grid = OccupancyGridMap.from_png("tests/maps/example_map_occupancy.png", 1)
    grid = OccupancyGridMap.from_png("tests/maps/track.png", 1)

    # Place robot in the world
    grid.world[start_pos[0]:start_pos[0] + dim_robot,
               start_pos[1]:start_pos[1] + dim_robot] = 1

    step_size = 5
    current_pos = start_pos
    for step in range(50):
        y, x = current_pos

        next_y, next_x = (step_size + y), (step_size + x)

        # Reset visited pixels
        grid.world[y:y+dim_robot, x:x+dim_robot] = 0


        obstacles = detect_collision((next_y, next_x), grid)
        if sum(obstacles) > 0:
            print("Detected obstacles at:", obstacles)
        
        # Marks robots new cells
        grid.world[next_y:next_y+dim_robot, next_x:next_x+dim_robot] = 1
        current_pos = (next_y, next_x)
        
        grid.plot()
        plt.pause(0.0001)
        plt.clf()

    grid.plot()
    plt.show(block=True)
    plt.show()

if __name__ == "__main__":
    main()
