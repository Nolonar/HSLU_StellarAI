"""
Test `Robot` model.
"""
import numpy as np
from pytest import fixture
from stellar.models.robot import Robot

from hypothesis import given
import hypothesis.strategies as some


@fixture
def robot():
    return Robot()


def test_robot_initializes_at_origin(robot):
    assert robot.x == robot.y == robot.theta == 0.0
