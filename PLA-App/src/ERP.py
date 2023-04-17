
import multiprocessing
import signal
import sys
from modules import udp_comm_class, terminal_class, database_orders_class
from rich.traceback import install
install(show_locals=True)

# Constants
UDP_IP = "127.0.0.1"  # local
UDP_PORT = 54321

def process_orders():
    orders_obj = udp_comm_class.ProcessOrders(UDP_IP, UDP_PORT)
    orders_obj.start()


if __name__ == '__main__':
    try:
        #p = multiprocessing.Process(target=process_orders)
        #p.start()
        signal.signal(signal.SIGINT, signal_handler)
        terminal = terminal_class.ErpTerminal()
        terminal.run()
    except KeyboardInterrupt:
        print("Caught KeyboardInterrupt, terminating ERP")
        #p.terminate()
        sys.exit(0)

