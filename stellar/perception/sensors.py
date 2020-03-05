"""
Handle inbound communication from the tinyK22.

The tinyK22 sends bundled sensor data over an UART serial interface.
These messages are demodulated here into distinct values.
"""
import struct


def decode_blob(blob: bytes):
    """Decode sensor data array from tinyK22."""
    try:
        return struct.unpack("fff", blob)
    except struct.error:
        import binascii
        error_blob = binascii.hexlify(bytearray(blob))
        raise ValueError(f"Unable to decode data, got: {error_blob}")
