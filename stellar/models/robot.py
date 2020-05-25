
import numpy as np


class Robot:
    """Simple robot model."""

    def __init__(self):
        self.x = 0
        self.y = 0
        self.theta = 0

    def pose_in_grid(self, scale):
        """Converts the pose to the current position in the gridmap."""
        xr = int(self.x / scale)
        yr = int(self.y / scale)
        theta = np.radians(self.theta)

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

        a = direction + self.theta
        x = self.x + (np.cos(a) * distance)
        y = self.y + (np.sin(a) * distance)

        robot = Robot()
        robot.set(x, y, a)
        return robot

    def set(self, new_x: float, new_y: float, new_theta: float):
        """Set the current robots pose.

        Args:
            new_x: New x coordinate
            new_y: New y coordinate
            new_theta: New theta (orientation) in degrees.

        Raises:
            ValueError if the new coordinates or theta is not possible.

        """
        self.x = float(new_x)
        self.y = float(new_y)
        self.theta = float(new_theta)

    def __str__(self):
        return f"Robot[x: {self.x}, y: {self.y}, theta: {self.theta}]"
