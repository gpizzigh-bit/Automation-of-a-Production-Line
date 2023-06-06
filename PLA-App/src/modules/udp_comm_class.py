"""
.. module:: udp_comm_class
   :platform: Unix, Windows
   :synopsis: Establish an UDP communication to retrieve the orders data.

.. moduleauthor:: Gabriel Pizzighini <up201800998@up.pt>


"""

import socket
import threading
import time
import xml.etree.ElementTree as ET
from rich.traceback import install
from .database_orders_class import Database, Orders

install(show_locals=True)


class SchedulerExe(threading.Thread):
    def __init__(self):
        super().__init__()
        self.signal_execution = False
        self.scheduler = None
        print("thread started.", end='')

    def run(self) -> None:
        while True:
            if self.signal_execution:
                #print("\nRunning Scheduler Once\n")
                self.scheduler.update_scheduler()
                self.signal_execution = False

    def run_scheduler(self):
        self.signal_execution = True

    def set_scheduler(self, scheduler):
        self.scheduler = scheduler


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
        self.scheduler = None
        self.new_order_signal = None
        self.ip = ip
        self.port = port
        self.SIG_UPDATE = False
        print(f" [UDP] Waiting for connection... over {self.ip} : {self.port} ")

    def __connect(self):
        sock = socket.socket(socket.AF_INET,  # Internet
                             socket.SOCK_DGRAM)  # UDP
        sock.bind((self.ip, self.port))
        self.__aux = True
        while self.__aux:
            data, _ = sock.recvfrom(1024)  # buffer size is 1024 bytes
            sock.close()  # close socket
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
        client = ET.fromstring(data)
        for orders in client:
            data_as_dict = orders.attrib.values()
            self._orders_list.append(orders.attrib)
        return self._orders_list

    def get_last_order(self):
        return self._orders_list[-1:]

    def start(self, scheduler):
        """
        Starts listening for an udp connection to retrieve data and send to the database.
        """
        db = Database()
        orders_obj = Orders()
        thread_scheduler = SchedulerExe()
        thread_scheduler.start()
        thread_scheduler.set_scheduler(scheduler)
        while True:
            self.new_order_signal = False
            orders_list = self.get()
            client_dict = orders_list[0]
            client_name = client_dict['NameId'].split()[1]  ## get only the name
            for orders_dict in orders_list[1:]:
                number = orders_dict['Number']
                work_piece = orders_dict['WorkPiece']
                quantity = orders_dict['Quantity']
                due_date = orders_dict['DueDate']
                late_pen = orders_dict['LatePen']
                early_pen = orders_dict['EarlyPen']
                client_id = client_dict['NameId']
                orders_obj.add_Order(number,
                                     work_piece,
                                     quantity,
                                     due_date,
                                     late_pen,
                                     early_pen,
                                     client_id)
            self.new_order_signal = True
            thread_scheduler.run_scheduler()
            #scheduler.update_scheduler()

    def get_signal_of_new_order(self):
        return self.new_order_signal

    def set_scheduler(self, mps):
        self.scheduler = mps
