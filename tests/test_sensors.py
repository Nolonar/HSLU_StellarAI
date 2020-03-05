"""
Tests for the communication between stellar and the tinyk22.
"""
import struct
import pytest
import numpy as np


from stellar.perception.sensors import decode_blob


def test_decode_sensor_data():
    sampled_sensor_data = [0.3, 0.2, 0.1]
    blob = struct.pack("fff", *sampled_sensor_data)

    expected = (0.3, 0.2, 0.1)
    got = decode_blob(blob)
    assert got == pytest.approx(expected, 0.001)

def test_should_raise_error_on_invald_data():
    sampled_sensor_data = [0.3, 0.2, 0.1]
    blob = struct.pack("ddd", *sampled_sensor_data)

    with pytest.raises(ValueError):
        print(decode_blob(blob))
    print(decode_blob(blob))
    assert False
