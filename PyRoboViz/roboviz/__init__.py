'''
roboviz.py - Python classes for displaying maps and robots

Requires: numpy, matplotlib

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

'''
# Essential imports
import matplotlib.pyplot as plt
import matplotlib.cm as colormap
import matplotlib.lines as mlines
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

# This helps with Raspberry Pi
import matplotlib
matplotlib.use('TkAgg')


class Visualizer(object):

    # Robot display params
    ROBOT_HEIGHT_M = 0.5
    ROBOT_WIDTH_M = 0.3

    def __init__(self, map_size_pixels, map_size_meters, title, show_trajectory=False, zero_angle=0):

        # Put origin in center
        # self._init(map_size_pixels, map_size_meters, title, -map_size_pixels / 2, show_trajectory, zero_angle)
        self._init(map_size_pixels, map_size_meters, title, -
                   map_size_pixels / 2, show_trajectory, zero_angle)

    def display(self, x_m, y_m, theta_deg):

        self._setPose(x_m, y_m, theta_deg)

        return self._refresh()

    def show_pylon(self, target):
        x, y = target
        x /= self.map_scale_meters_per_pixel
        y /= self.map_scale_meters_per_pixel
        self.ax.plot(x, y, marker='^', color='orange', markersize=12)

    def show_beam(self, target):
        """
        Show ultrasonic beam (simplified).
        """
        x, y = target
        self.ax.plot(x, y, marker='x', color='red')

    def _init(self, map_size_pixels, map_size_meters, title, shift, show_trajectory=False, zero_angle=0, reference_trajectory=None):

        # Store constants for update
        map_size_meters = map_size_meters
        self.map_size_pixels = map_size_pixels
        self.map_scale_meters_per_pixel = map_size_meters / \
            float(map_size_pixels)

        # Create a byte array to display the map with a color overlay
        self.bgrbytes = bytearray(map_size_pixels * map_size_pixels * 3)

        # Make a nice big (10"x10") figure
        fig = plt.figure(figsize=(10, 10))

        # Store Python ID of figure to detect window close
        self.figid = id(fig)

        fig.canvas.set_window_title(title)
        plt.title(title)

        # Use an "artist" to speed up map drawing
        self.img_artist = None

        # No vehicle to show yet
        self.vehicle = None

        # Create axes
        self.ax = fig.gca()
        self.ax.set_xlabel('X (m)')
        self.ax.set_ylabel('Y (m)')

        if reference_trajectory is not None:
            self.ax.plot(
                reference_trajectory[:, 0], reference_trajectory[:, 1], 'r')

        # Hence we must relabel the axis ticks to show millimeters
        # + 100 to show endpoints
        ticks = np.arange(shift, self.map_size_pixels + shift + 100, 25)
        labels = [str(self.map_scale_meters_per_pixel * tick)
                  for tick in ticks]
        self.ax.set_xticklabels(labels)
        self.ax.set_yticklabels(labels)

        minor_ticks = np.arange(shift, self.map_size_pixels+shift+100, 2.5)
        self.ax.set_yticks(minor_ticks, minor=True)
        self.ax.set_xticks(minor_ticks, minor=True)
        self.ax.grid(b=True, which='major', alpha=0.5, color='black')
        self.ax.grid(b=True, which='minor', alpha=0.3, color='gray')
        # Store previous position for trajectory
        self.prevpos = None
        self.showtraj = show_trajectory

        # We base the axis on pixels, to support displaying the map
        self.ax.set_xlim([shift, self.map_size_pixels+shift])
        self.ax.set_ylim([shift, self.map_size_pixels+shift])

        # Set up default shift for centering at origin
        shift = -self.map_size_pixels / 2

        self.zero_angle = zero_angle
        self.start_angle = None
        self.rotate_angle = 0

    def _setPose(self, x_m, y_m, theta_deg):
        '''
        Sets vehicle pose:
        X:      left/right   (m)
        Y:      forward/back (m)
        theta:  rotation (degrees)
        '''

        # If zero-angle was indicated, grab first angle to compute rotation
        if self.start_angle is None and self.zero_angle != 0:
            self.start_angle = theta_deg
            self.rotate_angle = self.zero_angle - self.start_angle

        # Rotate by computed angle, or zero if no zero-angle indicated
        d = self.rotate_angle
        a = np.radians(d)
        c = np.cos(a)
        s = np.sin(a)
        x_m, y_m = x_m*c-y_m*s, y_m*c+x_m*s

        # Erase previous vehicle image after first iteration
        if not self.vehicle is None:
            self.vehicle.remove()

        # Use a very short arrow shaft to orient the head of the arrow
        theta_rad = np.radians(theta_deg+d)
        c = np.cos(theta_rad)
        s = np.sin(theta_rad)
        l = 0.1
        dx = l * c
        dy = l * s

        s = self.map_scale_meters_per_pixel

        self.vehicle = self.ax.arrow(x_m/s, y_m/s,
                                     dx, dy, head_width=Visualizer.ROBOT_WIDTH_M/s,
                                     head_length=Visualizer.ROBOT_HEIGHT_M/s, fc='r', ec='r', zorder=5)

        # Show trajectory if indicated
        currpos = self._m2pix(x_m, y_m)
        if self.showtraj and not self.prevpos is None:
            self.ax.add_line(mlines.Line2D(
                (self.prevpos[0], currpos[0]), (self.prevpos[1], currpos[1])))
        self.prevpos = currpos

    def _refresh(self):

        # If we have a new figure, something went wrong (closing figure failed)
        if self.figid != id(plt.gcf()):
            return False

        # Redraw current objects without blocking
        plt.draw()

        # Refresh display, setting flag on window close or keyboard interrupt
        try:
            plt.pause(.01)  # Arbitrary pause to force redraw
            return True
        except:
            return False

        return True

    def _pix2m(self, x, y):
        s = self.map_scale_meters_per_pixel
        return x * s, y * s

    def _m2pix(self, x_m, y_m):

        s = self.map_scale_meters_per_pixel

        return x_m/s, y_m/s


class MapVisualizer(Visualizer):

    def __init__(self, map_size_pixels, map_size_meters, title='MapVisualizer', show_trajectory=False, reference_trajectory=None):

        # Put origin in lower left; disallow zero-angle setting
        Visualizer._init(self, map_size_pixels, map_size_meters,
                         title, 0, show_trajectory, 0, reference_trajectory=reference_trajectory)

    def display(self, robot, mapbytes, vmin, vmax):
        x, y = self._pix2m(robot.x, robot.y)
        self._setPose(x, y, np.degrees(robot.theta))

        # Pause to allow display to refresh

        if self.img_artist is None:
            self.img_artist = self.ax.imshow(
                mapbytes, vmin=vmin, vmax=vmax, cmap='gray_r')
        else:
            self.img_artist.set_data(mapbytes)

        # plt.pause(.01)
        return self._refresh()
