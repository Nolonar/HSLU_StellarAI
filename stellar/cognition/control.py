"""
Contains motion control logic.

PID Control
===========

P: Proportional

Problem: How to steer the vehicle? Assume: Velocity is constant

Crosstrack error (CTE)
----------------------
The crosstrack error is the difference between the robot position and a
reference trajectory (i.e. the planned path)

The greater this error is, the more the vehicle has to steer to this reference.

"""
