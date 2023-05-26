import socket
import pickle

global_ip = "127.0.0.1"
global_port = 12345


class TCPClient:
    def __init__(self):
        self.ip = global_ip
        self.port = global_port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect()
        print(f" [TCP CLIENT] Waiting for connection... over {self.ip} : {self.port} ")

    def connect(self):
        self.socket.connect((self.ip, self.port))

    def send(self, message):
        data = pickle.dumps(message)
        self.socket.send(data)

    def receive(self, buffer_size):
        return self.socket.recv(buffer_size)

    def close(self):
        self.socket.close()


class TCPServer:
    def __init__(self):
        self.ip = global_ip
        self.port = global_port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print(f" [TCP] Waiting for connection... over {self.ip} : {self.port} ")
        self.socket.bind((self.ip, self.port))
        self.socket.listen(1)
        self.connection, self.address = self.socket.accept()

    def receive(self, buffer_size):
        return pickle.loads(self.connection.recv(buffer_size))

    def send(self, message):
        data = pickle.dumps(message)
        self.connection.send(data)

    def close(self):
        self.connection.close()
        self.socket.close()
