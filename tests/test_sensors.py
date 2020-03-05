"""
Tests for the communication between stellar and the tinyk22.
"""
import struct
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


def test_decode_sensor_data(tinyk):
    sampled_sensor_data = [0.3, 0.2, 0.1]
    blob = struct.pack("fff", *sampled_sensor_data)

    expected = (0.3, 0.2, 0.1)

    assert tinyk.process_blob(blob) == pytest.approx(expected, 0.001)