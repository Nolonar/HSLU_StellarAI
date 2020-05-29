
import numpy as np


class Robot:
    """
    Simple model for our robot.
    """

    def __init__(self):
        """
        Initalize the robot with the starting values of (0, 0, 0) for 
        position (x, y) and orientation (theta).
        """
        self.x = 0.0
        self.y = 0.0
        self.theta = 0.0

    def pose_in_grid(self, scale):
        """Converts the pose to the current position in the gridmap."""
        xr = int(self.x / scale)
        yr = int(self.y / scale)
        theta = self.theta

        return (xr, yr, theta)

    def move(self, distance: int, direction: float, max_steering=np.pi / 2):
        """Instruct the robot to move.

        Args:
            distance: Number of steps (i.e. cells) to move.
            direction: Direction of movement (in radians)

        Returns:
            The robots new pose (x, y, theta).

        """
        if direction > max_steering:
            direction = max_steering
        if direction < -max_steering:
            direction = -max_steering

        if distance < 0.0:
            distance = 0.0

        self.theta += direction
        self.x = self.x + (np.cos(self.theta) * distance)
        self.y = self.y + (np.sin(self.theta) * distance)

    def set(self, x: float, y: float, theta: float):
        """Change the robots current pose.

        Args:
            x: New x coordinate
            y: New y coordinate
            theta: New theta (orientation) in radians.

        Raises:
            ValueError if the new coordinates or theta is not possible.

        """
        self.x = float(x)
        self.y = float(y)
        self.theta = float(theta)

    def __str__(self):
        return f"Robot[x: {self.x}, y: {self.y}, theta: {self.theta}]"
