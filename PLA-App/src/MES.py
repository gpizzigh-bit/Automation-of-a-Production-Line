# [TODO] Communicate to the Database
# [TODO] Lost Communication retrive "Last state" from the database
# [TODO] Execute Orders

import multiprocessing
from modules import tcp_comm

from opcua import Client

url = "opc.tcp://localhost:4840"
client = Client(url)


def process_tcp_comm():
    client = tcp_comm.TCPClient()
    print("receiving...")
    client.connect()
    while True:
        message = client.receive(1024)
        print(f"Received: {message}")


if __name__ == '__main__':
    tcp_process = multiprocessing.Process(target=process_tcp_comm)
    tcp_process.start()


    try:
        # Connect to server
        client.connect()

        # Read node
        var = client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.Geral.Enter_Piece_Up0.cmd_L")
        print(f'Value of node : {var.get_value()}')

        # Change value
        var.set_value(False)
        print(f'New value is : {var.get_value()}')


    finally:
        client.disconnect()

