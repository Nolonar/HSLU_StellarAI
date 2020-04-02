"""
Handle inbound communication from the tinyK22.

This module takes in a binary stream and returns concrete values, as recorded
by the array of sensors connected to the tinyK22.

The tinyK22 sends bundled sensor data over an UART serial interface. These
messages are demodulated here into distinct values. A UART message consists
of a start bit, 8 bits of data and a stop bit. Multiple messages can be send
indipendently until the stop bit is set.

Multiple steps are performed read and parse UART messages:
    1. Read raw binary data from the device
    2. Reassemble original payload from fragmented messages
    3. Reconstruct original payload by parsing the binary blobs.

"""
import io
import queue
import struct
from typing import List


def decode_blob(blob: bytes, fmt="=ffffii"):
    """Decode sensor data array from tinyK22.

    NOTE: No error is raised if the byte length matches, e.g. "=ffffii"
    matches "=ddd" well, so no error is raised. Perform sanity checks.
    """
    try:
        return struct.unpack(fmt, blob)
    except struct.error:
        import binascii
        error_blob = binascii.hexlify(bytearray(blob))
        raise ValueError(f"Unable to decode data, got: {error_blob}")


def combine_messages(blobs: List[bytes]) -> bytes:
    """Combines multiple UART messages into a single data buffer.

    Assumes structure described in the module docstring. Start- and
    """
    buf = []
    for blob in blobs:
        stop_bit = blob[-1]
        buf.append(blob[1:9])

        if stop_bit == 0x01:
            break

    return b''.join(buf)


def send_data_to_observatory(data: dict):
    """Sends data to observatory"""

    import socket
    import json

    # AF_UNIX is a lightweight method for interprocess communication,
    # but it is only available on UNIX systems.
    # For testing on Windows, we can use INET as alternative.
    socket_address_family = getattr(socket, 'AF_UNIX', socket.AF_INET)
    address = (
        'localhost', 55555) if socket_address_family == socket.AF_INET else 'tmp/stellar/perception/sensors'

    sender_socket = socket.socket(socket_address_family, socket.SOCK_STREAM)
    sender_socket.connect(address)
    sender_socket.sendall(json.dumps(data).encode('utf-8'))
    sender_socket.close()


class Sensors:
    """Continuously read sensor data from the tinyK22."""

    def __init__(self, device: io.BytesIO, out_queue: queue.Queue, fmt="=xffffiix"):
        self.device = device
        self.out_queue = out_queue
        self.fmt = fmt

    def read(self):
        """Reads and decodes sensor signals."""
        blob = self.device.read()
        if blob:
            values = decode_blob(blob, self.fmt)
            self.out_queue.put(values)

    import datetime
    time_created = datetime.datetime.now()  # temp

    def get_mock_data(self) -> dict:
        """Returns mock data to be sent to observatory."""
        import random
        import datetime
        return {
            'time': {
                'current': (datetime.datetime.now() - self.time_created).seconds * 1000,
                'best': (datetime.datetime.now() - self.time_created).seconds * 1000
            },
            'battery': 99,
            'map': None,
            'cameraFeed': None,
            'sensorMech': {
                'motor': random.randint(0, 1600),
                'steering': random.randint(-90, 90)
            },
            'sensorElec': {
                'cpu': {
                    'load': [
                        random.randint(0, 100),
                        random.randint(0, 100),
                        random.randint(0, 100),
                        random.randint(0, 100)
                    ],
                    'temp': random.randint(0, 100)
                },
                'ram': random.randint(0, 100)
            }
        }


if __name__ == '__main__':
    import time

    sensors = Sensors(None, None)  # temporary

    while True:
        time.sleep(1)
        send_data_to_observatory(sensors.get_mock_data())
