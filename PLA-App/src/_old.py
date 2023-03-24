# [DONE] Open communication over UDP/IP port 54321 to receive xml 
# [DONE] read from xml file and extract clients request
# [TODO] build terminal
# [TODO] Create the Production Plan
# [TODO] Communicate to the Database
# [TODO] Lost Communication retrive "Last state" from the database
# [TODO] Communicate to the MES (Server-side)

# Global Modules
import socket
import xml.etree.ElementTree as ET
import threading
from rich.traceback import install

install(show_locals=True)

# Local Modules
from modules import udp_comm_class

# Constants
UDP_IP = "127.0.0.1"  # local
UDP_PORT = 54321

# global variables
orders


def threaded_udp_connection(udp_ip, udp_port):
    # Run in loop waiting for connection
    # if connection found signal that there is data to be consumed
    orders_obj = udp_comm_class.ProcessOrders(udp_ip, udp_port)
    global orders
    orders = orders_obj.get()
    print("sent data to the orders database")
#   send this data to the database


if __name__ == "__main__":
    comm_thread = threading.Thread(target=threaded_udp_connection, args=(UDP_IP, UDP_PORT), daemon=True)
    comm_thread.start()
    cnt = 0
    while True:
        pass
    # comm_thread.join()
    # print(orders[0]["Number"])
