# [DONE] Open communication over UDP/IP port 54321 to receive xml 
# [DONE] read from xml file and extract clients request
# [TODO] build terminal
# [TODO] Create the Production Plan
# [TODO] Communicate to the Database
# [TODO] Lost Communication retrive "Last state" from the database
# [TODO] Communicate to the MES (Server-side)

#Global Modules
import socket
import xml.etree.ElementTree as ET
from rich.traceback import install
install(show_locals=True)

#Local Modules
from modules import udp_comm_class

# Constants
UDP_IP = "127.0.0.1" # local
UDP_PORT = 54321

orders_obj = udp_comm_class.Orders(UDP_IP,UDP_PORT)
orders = orders_obj.get()
print(orders[0]["Number"])