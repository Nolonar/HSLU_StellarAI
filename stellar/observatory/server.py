import json
import os.path
import pathlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

hostName = 'localhost'
serverPort = 8080


class Server(BaseHTTPRequestHandler):
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


if __name__ == '__main__':
    with ThreadingHTTPServer((hostName, serverPort), Server) as server:
        print('Server listening on port: {}'.format(serverPort))
        server.serve_forever()
