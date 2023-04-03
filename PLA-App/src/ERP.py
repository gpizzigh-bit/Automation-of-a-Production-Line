
import multiprocessing
from modules import udp_comm_class, terminal_class
from rich.traceback import install
install(show_locals=True)

# Constants
UDP_IP = "127.0.0.1"  # local
UDP_PORT = 54321

def process_orders():
    orders_obj = udp_comm_class.ProcessOrders(UDP_IP, UDP_PORT)
    orders_obj.start()


if __name__ == '__main__':
    # p = multiprocessing.Process(target=process_orders)
    # p.start()
    terminal = terminal_class.ErpTerminal()
    terminal.run()
