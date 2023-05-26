import multiprocessing
import sys
import threading
import time

from rich.traceback import install

from constants.local_constants import erp_to_mes_test_data

from modules import tcp_comm, MPS
from modules import udp_comm_class, terminal_class

install(show_locals=True)

# Constants
UDP_IP = "127.0.0.1"  # local
UDP_PORT = 54321

TCP_IP = "127.0.0.1"  # local
TCP_PORT = 12345

FEEDBACK_MSG = "Message Received!"
HANDSHAKE_FROM_ERP = "HANDSHAKE FROM ERP"

day_time = 60

mps = MPS.Scheduler()


class ThreadedClient(threading.Thread):
    def __init__(self):
        # create a client object to communicate with the server
        super().__init__()
        self.client = tcp_comm.TCPClient()
        self.signal_to_stop = False
        self.msg = None
        self.feedback_msg = None

    def run(self) -> None:
        while self.signal_to_stop is not True:
            self.client.send(self.msg)
            self.feedback_msg = self.client.receive(1024)

    def set_msg(self, msg):
        self.msg = msg

    def get_feedback_mgs(self):
        return self.feedback_msg

    def stop(self):
        self.signal_to_stop = True


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
    comm_to_mes = ThreadedClient()
    comm_to_mes.start()
    day_index = 0
    try:
        # initialize terminal
        # terminal.show_new_plans(mps)
        # terminal.run()

        mps.first_run()
        terminal.show_new_plans(mps)
        # mps.show_schedule()

        current_time = start_time = time.monotonic()
        next_time = start_time + 2
        while current_time - start_time <= day_time:
            current_time = time.monotonic()
            # print(current_time - start_time)
            if current_time - start_time >= day_time:
                # day is over reset start time
                day_index += 1
                if day_index >= len(erp_to_mes_test_data):
                    sys.exit(1)
                print(
                    f"------------------------------------------------ day: {day_index} "
                    f"---------------------------------------")
                # mps.show_schedule()
                start_time = current_time
                next_time = start_time + 2
                # lock the current day on the mps and re-run the algorithm
                mps.request_lock_current_day = True
                mps.lock_current_day()
                mps.run()
                #
            elif current_time >= next_time:
                next_time += 2
                # current day is running...
                # after 2 seconds
                # send today orders to the ERP and wait a feedback

                comm_to_mes.set_msg(erp_to_mes_test_data[day_index])
            continue

        p.kill()
        sys.exit(1)
    except KeyboardInterrupt:
        terminal.exit(0, "Caught KeyboardInterrupt, terminating Terminal")
        print("Caught KeyboardInterrupt, terminating ERP")
        p.kill()
        # tcp_process.kill()
        sys.exit(1)
