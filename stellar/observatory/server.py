import json
import os.path
import pathlib
import socket
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread

hostName = 'localhost'
serverPort = 8080

rootPath = os.path.join(pathlib.Path(__file__).parent, 'debug-ui')

debug_data: dict = None
is_server_running = True


class RequestHandler(BaseHTTPRequestHandler):
    routes = {
        '/': lambda self: self.send_file('/index.html'),
        '/debug-data': lambda self: self.send_debug_data()
    }

    def do_GET(self):
        if self.path in self.routes:
            self.routes[self.path](self)
        else:
            self.send_file(self.path)

    def send_file(self, path):
        try:
            file_to_open = os.path.join(rootPath, path[1:])
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


def listen_to_socket():
    global debug_data

    # AF_UNIX is a lightweight method for interprocess communication,
    # but it is only available on UNIX systems.
    # For testing on Windows, we can use INET as alternative.
    socket_address_family = getattr(socket, 'AF_UNIX', socket.AF_INET)
    address = (
        '', 55555) if socket_address_family == socket.AF_INET else 'tmp/stellar/perception/sensors'

    listener_socket = socket.socket(socket_address_family, socket.SOCK_STREAM)
    listener_socket.bind(address)
    listener_socket.listen()

    while is_server_running:
        connection, _ = listener_socket.accept()
        received_data = connection.recv(1024).decode('utf-8')
        debug_data = json.loads(received_data)
        connection.close()


if __name__ == '__main__':
    Thread(target=listen_to_socket).start()

    try:
        with ThreadingHTTPServer((hostName, serverPort), RequestHandler) as server:
            print('Server listening on port: {}'.format(serverPort))
            server.serve_forever()
    except:
        is_server_running = False
