"""
.. module:: udp_comm_class
   :platform: Unix, Windows
   :synopsis: Establish an UDP communication to retrieve the orders data.

.. moduleauthor:: Gabriel Pizzighini <up201800998@up.pt>


"""

import socket
import xml.etree.ElementTree as ET
from rich.traceback import install
from .database_orders_class import Database, Orders

install(show_locals=True)


class ProcessOrders:
    """
    Class that retrieves orders from a udp connection server client XML file

    :method get():
        :return: list of orders from the connection socket
        :rtype: list[dic]
    """

    __aux = True
    _orders_list = []

    def __init__(self, ip, port) -> None:
        """
        Class constructor

        Args:
            ip (str): ip to establish the udp connection
            port (int): port for establishing an udp connection
        """
        self.ip = ip
        self.port = port
        self.SIG_UPDATE = False
        pass

    def __connect(self):
        print("Waiting for connection...")
        self.__aux = True
        sock = socket.socket(socket.AF_INET,  # Internet
                             socket.SOCK_DGRAM)  # UDP
        sock.bind((self.ip, self.port))

        while self.__aux:
            data, _ = sock.recvfrom(1024)  # buffer size is 1024 bytes
            sock.close()
            self.__aux = False  # exit loop
        return data

    def get(self):
        """
        Retrieves the data from the connection
        
        Returns:  
            list (dic) -- the orders in a list of dictionary.
        """
        data = self.__connect()
        self._orders_list = []
        #print("Received:", data)
        client = ET.fromstring(data)
        for orders in client:
            #print("Received:", orders.attrib)
            data_as_dict = orders.attrib.values()
            #print(data_as_dict)
            self._orders_list.append(orders.attrib)
        return self._orders_list

    def start(self):
        """
        Starts listening for an udp connection to retrieve data and send to the database.
        """
        db = Database()
        orders_obj = Orders()
        while True:
            orders_list = self.get()
            client_dict = orders_list[0]
            client_name = client_dict['NameId'].split()[1] ## get only the name
            # [TODO] Remove this
            match client_name:
                case "AA":
                    client_id = 1
                case "BB":
                    client_id = 2
                case "CC":
                    client_id = 3
                case "DD":
                    client_id = 4
                case _:
                    client_id = 0
            for orders_dict in orders_list[1:]:
                number = orders_dict['Number']
                work_piece = orders_dict['WorkPiece']
                quantity = orders_dict['Quantity']
                due_date = orders_dict['DueDate']
                late_pen = orders_dict['LatePen']
                early_pen = orders_dict['EarlyPen']
                orders_obj.add_Order(number,
                                     work_piece,
                                     quantity,
                                     due_date,
                                     late_pen,
                                     early_pen,
                                     client_id)
                #print(orders_dict)
            #print(orders_list)
