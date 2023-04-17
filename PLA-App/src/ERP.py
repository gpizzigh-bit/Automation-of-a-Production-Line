import multiprocessing
import signal
import sys
import threading
from modules import udp_comm_class, terminal_class, database_orders_class
from modules import tcp_comm
from rich.traceback import install
from time import monotonic

install(show_locals=True)

# Constants
UDP_IP = "127.0.0.1"  # local
UDP_PORT = 54321


def process_tcp_comm():
    server = tcp_comm.TCPServer()
    start_time = monotonic()
    print(start_time)
    while True:
        time = monotonic() - start_time
        _, seconds = divmod(time, 60)
        if seconds >= 52:
            server.send("End of day")
            start_time = monotonic()


def process_orders():
    orders_obj = udp_comm_class.ProcessOrders(UDP_IP, UDP_PORT)
    orders_obj.start()


if __name__ == '__main__':
    try:
        p = multiprocessing.Process(target=process_orders)
        p.start()
        tcp_process = multiprocessing.Process(target=process_tcp_comm)
        tcp_process.start()
        terminal = terminal_class.ErpTerminal()
        terminal.run()
    except KeyboardInterrupt:
        print("Caught KeyboardInterrupt, terminating ERP")
        sys.exit(0)
