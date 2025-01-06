import os
import socket


class Connector:
    def __init__(self, socket_file):
        self.socket_file = socket_file

    def is_alive(self):
        if not self.socket_file:
            return False
        if not os.path.exists(self.socket_file):
            return False
        try:
            response = self.send("status")
        except ConnectionRefusedError:
            return False
        if not response:
            return False
        return True

    def send(self, command: str):
        _socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            _socket.connect(self.socket_file)
            _socket.send(command.encode())
            response = _socket.recv(1024)
            return response.decode()
        finally:
            _socket.close()
