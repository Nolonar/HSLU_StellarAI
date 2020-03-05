import json
import socket

sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

diagnostics = {
        "current_position": (0.0, 0.1, 0.3),
        "speed": "lighting-speed"
}

data = json.dumps(diagnostics)

sock.connect('/tmp/unixSocket')
sock.sendall(data)
