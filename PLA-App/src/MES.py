# [TODO] Communicate to the ERP (Client-side)
# [TODO] Communicate to the MODBUS interface (OPC-UA over IP)
# [TODO] Communicate to the Database
# [TODO] Lost Communication retrive "Last state" from the database
# [TODO] Execute Orders

import multiprocessing
from modules import tcp_comm


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
    # continue the code...
