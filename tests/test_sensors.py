"""
Tests for the communication between stellar and the tinyk22.
"""
import pytest
import numpy as np

from stellar.perception.sensors import TinyK


@pytest.fixture
def tinyk():
    # More setup code here
    return TinyK()


def test_should_process_sensor_array(tinyk):
    """
    This is just a dummy test.
    """
    values = tinyk.process()
    assert isinstance(values, np.ndarray)
