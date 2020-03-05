"""
Handle inbound communication from the tinyK22.

The tinyK22 sends bundled sensor data over an UART serial interface.
These messages are demodulated here into distinct values.
"""
import struct
import numpy as np


class TinyK(object):
    """
    Dummy object for testing.
    """

    def process_blob(self, blob: bytes):
        return struct.unpack("fff", blob)


    def process(self) -> np.ndarray:
        """Process an incoming message."""
        return np.array([0.1, 0.1, 0.0])