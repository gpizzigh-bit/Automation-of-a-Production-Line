import socket

global_ip = "127.0.0.1"
global_port = 12345

class TCPClient:
    def __init__(self):
        self.ip = global_ip
        self.port = global_port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        self.socket.connect((self.ip, self.port))

    def send(self, message):
        self.socket.send(message.encode())

    def receive(self, buffer_size):
        return self.socket.recv(buffer_size).decode()

    def close(self):
        self.socket.close()


class TCPServer:
    def __init__(self):
        self.ip = global_ip
        self.port = global_port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.ip, self.port))
        self.socket.listen(1)
        self.connection, self.address = self.socket.accept()

    def receive(self, buffer_size):
        return self.connection.recv(buffer_size).decode()

    def send(self, message):
        self.connection.send(message.encode())

    def close(self):
        self.connection.close()
        self.socket.close()



