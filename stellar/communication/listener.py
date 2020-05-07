import hashlib
import json
import socket
from threading import Thread
from typing import Any, Callable


class MessageListener:
    handler: Callable[[dict], Any]
    listener_socket: socket
    is_running: bool = True

    def __init__(self, sender_id: str, callback: Callable[[dict], Any]):
        self.handler = callback

        windows_address = ('localhost', 55555)
        unix_address = f'tmp/stellar/{sender_id}'

        # AF_UNIX is a lightweight method for interprocess communication,
        # but it is only available on UNIX systems.
        # For testing on Windows, we can use INET as alternative.
        socket_address_family = getattr(socket, 'AF_UNIX', socket.AF_INET)
        address = windows_address if socket_address_family == socket.AF_INET else unix_address

        self.listener_socket = socket.socket(
            socket_address_family, socket.SOCK_STREAM)
        self.listener_socket.bind(address)
        self.listener_socket.listen()

    def run(self):
        while self.is_running:
            connection, _ = self.listener_socket.accept()
            received_data = connection.recv(1024).decode('utf-8')
            self.handler(json.loads(received_data))
            connection.close()

    def stop(self):
        self.is_running = False


def listen_to(sender_id: str, listener: Callable[[dict], Any]) -> MessageListener:
    """
    Registers a listener for messages sent by sender_id.
    """

    message_listener = MessageListener(sender_id, listener)
    Thread(target=message_listener.run).start()
    return message_listener
