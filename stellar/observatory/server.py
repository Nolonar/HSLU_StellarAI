import json
import os.path
import pathlib
import socket
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread

hostName = 'localhost'
serverPort = 8080

debug_data = None


class RequestHandler(BaseHTTPRequestHandler):
    rootPath = os.path.join(pathlib.Path(__file__).parent, 'debug-ui')

    routes = {
        '/debug-data': lambda self: self.send_debug_data()
    }

    def do_GET(self):
        if self.path in self.routes:
            self.routes[self.path](self)
            return

        if self.path == '/':
            self.path = '/index.html'

        try:
            file_to_open = os.path.join(self.rootPath, self.path[1:])
            content_to_send = open(file_to_open).read()
            self.send_response(200)
        except:
            content_to_send = 'File not found'
            self.send_response(404)

        self.end_headers()
        self.wfile.write(bytes(content_to_send, 'utf-8'))

    def send_debug_data(self):
        self.send_response(200)
        self.send_header('Content-Type', 'text/plain')
        self.end_headers()
        self.wfile.write(
            bytes(json.dumps(self.get_debug_data(), default=str), 'utf-8'))

    def get_debug_data(self):
        return debug_data

        import random
        import datetime
        return {
            'time': {
                'current': datetime.datetime.now().time(),
                'best': datetime.datetime.now().time()
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


def listen_to_socket():
    # AF_UNIX is a lightweight method for interprocess communication,
    # but it is only available on UNIX systems.
    # For testing on Windows, we can use INET as alternative.
    socket_address_family = getattr(socket, 'AF_UNIX', socket.AF_INET)
    address = (
        '', 55555) if socket_address_family == socket.AF_INET else 'tmp/stellar/debug'

    listener_socket = socket.socket(socket_address_family, socket.SOCK_STREAM)
    listener_socket.bind(address)
    listener_socket.listen()

    while True:
        client_socket, _ = listener_socket.accept()
        debug_data = client_socket.recv(1024)
        client_socket.close()


if __name__ == '__main__':
    Thread(target=listen_to_socket).start()

    with ThreadingHTTPServer((hostName, serverPort), RequestHandler) as server:
        print('Server listening on port: {}'.format(serverPort))
        server.serve_forever()
