import multiprocessing
import signal
import sys
import threading
import time

from modules import udp_comm_class, terminal_class, database_orders_class
from modules import tcp_comm, MPS
from rich.traceback import install
from time import monotonic

install(show_locals=True)

# Constants
UDP_IP = "127.0.0.1"  # local
UDP_PORT = 54321

mps = MPS.Scheduler()


class CommunicateToMES(threading.Thread):

    def __init__(self):
        super().__init__()
        self.server = tcp_comm.TCPServer()

    def run(self):
        # server = tcp_comm.TCPServer()
        # while True:
        #     time = monotonic() - start_time
        #     _, seconds = divmod(time, 60)
        #     if seconds >= 52:
        #         server.send("End of day")
        #         start_time = monotonic()
        print(mps.current_day)
        test = [{'workpiece': 'P7', 'status': 'store2deliver'},
                {'workpiece': 'P7', 'status': 'store2deliver'},
                {'workpiece': 'P7', 'status': 'store2deliver'},
                {'workpiece': 'P6', 'status': 'makeANDdeliver'}]
        self.server.send(test)
        print("sent data to client")


def process_orders():
    orders_obj = udp_comm_class.ProcessOrders(UDP_IP, UDP_PORT)
    orders_obj.start()


def pass_to_next_day():
    mps.request_lock_current_day = True
    mps.run()
    print("next day...")
    # tcp_process.start()
    # tcp_process.join()


if __name__ == '__main__':
    terminal = terminal_class.ErpTerminal()
    p = multiprocessing.Process(target=process_orders)
    p.start()
    tcp_comm_with_mes = CommunicateToMES()
    # tcp_process = multiprocessing.Process(target=process_tcp_comm)
    try:
        # initialize terminal
        # terminal.show_new_plans(mps)
        # terminal.run()

        mps.first_run()
        terminal.show_new_plans(mps)
        # mps.show_schedule()

        tcp_comm_with_mes.start()

        for day_index in range(5):
            print()
            print(
                f"------------------------------------------------ day: {day_index} ---------------------------------------")
            time.sleep(3)
            pass_to_next_day()
            terminal.show_new_plans(mps)
            # tcp_process.join()
            tcp_comm_with_mes.run()
            print(f"current day: {mps.current_day}")
            print(f"----------------------------------------------------------------------------------------------")
            print()

        # time.sleep(10)
        # pass_to_next_day()
        # time.sleep(10)
        # pass_to_next_day()
        # time.sleep(10)
        # print(mps.current_day)
        # print()
        # mps.show_schedule()

        # tcp_process.start()
        p.kill()
        # tcp_process.kill()
        sys.exit(1)
    except KeyboardInterrupt:
        terminal.exit(0, "Caught KeyboardInterrupt, terminating Terminal")
        print("Caught KeyboardInterrupt, terminating ERP")
        p.kill()
        # tcp_process.kill()
        sys.exit(1)
