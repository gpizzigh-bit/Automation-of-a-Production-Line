import socket
import xml.etree.ElementTree as ET
from rich.traceback import install
install(show_locals=True)


class Orders:

    __aux = True
    _orders_list = []

    def __init__(self,ip,port) -> None:
        self.ip = ip
        self.port = port
        pass

    def __connect(self):
        sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
        sock.bind((self.ip, self.port))

        while self.__aux:
            data, _ = sock.recvfrom(1024) # buffer size is 1024 bytes
            sock.close()
            self.__aux = False
        return data
    
    def get(self):
        data = self.__connect()
        client = ET.fromstring(data)
        for orders in client:
            self._orders_list.append(orders.attrib)
        return self._orders_list
