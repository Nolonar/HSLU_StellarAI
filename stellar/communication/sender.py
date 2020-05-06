import hashlib
import json
import socket


def send_message(sender_id: str, message: dict) -> bool:
    """
    Sends a message to whoever is listening.
    Returns False if nobody is listening, True otherwise.
    """

    windows_address = ('localhost', 55555)
    unix_address = f'tmp/stellar/{sender_id}'

    # AF_UNIX is a lightweight method for interprocess communication,
    # but it is only available on UNIX systems.
    # For testing on Windows, we can use INET as alternative.
    socket_address_family = getattr(socket, 'AF_UNIX', socket.AF_INET)
    address = windows_address if socket_address_family == socket.AF_INET else unix_address

    try:
        with socket.socket(socket_address_family, socket.SOCK_STREAM) as sender_socket:
            sender_socket.connect(address)
            sender_socket.sendall(json.dumps(message).encode('utf-8'))

    except:
        return False  # Nobody's listening right now.

    return True
