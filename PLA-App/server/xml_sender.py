import socket
import os
import xml.etree.ElementTree as ET
from rich.traceback import install
install(show_locals=True)

UDP_IP = "127.0.0.1" # local
UDP_PORT = 54321
tree = ET.parse('client_order.xml')
root = tree.getroot()
ORDER = ET.tostring(root)

print("UDP target IP: %s" % UDP_IP)
print("UDP target port: %s" % UDP_PORT)
print("order raw: %s" % ORDER)

sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
sock.sendto(ORDER, (UDP_IP, UDP_PORT))