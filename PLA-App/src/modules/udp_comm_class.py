"""
.. module:: udp_comm_class
   :platform: Unix, Windows
   :synopsis: Estabilish an UDP comunication to retrieve the orders data.

.. moduleauthor:: Gabriel Pizzighini <up201800998@up.pt>


"""



import socket
import xml.etree.ElementTree as ET
from rich.traceback import install
install(show_locals=True)


class Orders:
    """
    Class that retrieves orders from a udp connection server client XML file

    :method get():
        :return: list of orders from the connection socket
        :rtype: list[dic]
    """

    __aux = True
    _orders_list = []

    def __init__(self,ip,port) -> None:
        """
        Class constructor

        Args:
            ip (str): ip to estabilish the udp connection
            port (int): port for estabilishing an udp connection
        """
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
        """
        Retrives the data from the cennection
        
        Returns:  
            list (dic) -- the orders in a list of dictionaty.
        """
        data = self.__connect()
        client = ET.fromstring(data)
        for orders in client:
            self._orders_list.append(orders.attrib)
        return self._orders_list
