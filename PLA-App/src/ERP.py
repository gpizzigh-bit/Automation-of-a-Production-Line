import multiprocessing
import sys
import threading
import time

from rich.traceback import install

from constants.local_constants import erp_to_mes_test_data

from modules import tcp_comm, MPS
from modules import udp_comm_class, terminal_class

install(show_locals=True)

# TODO show the chosen supllier on the terminal

# Constants
UDP_IP = "127.0.0.1"  # local
UDP_PORT = 54321

TCP_IP = "127.0.0.1"  # local
TCP_PORT = 12345

FEEDBACK_MSG = "Message Received!"
HANDSHAKE_FROM_ERP = "HANDSHAKE FROM ERP"

day_time = 5

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

    def get_feedback_msg(self):
        return self.feedback_msg

    def stop(self):
        self.signal_to_stop = True


def process_orders():
    orders_obj = udp_comm_class.ProcessOrders(UDP_IP, UDP_PORT)
    orders_obj.start()


def pass_to_next_day():
    mps.request_lock_current_day = True
    mps.run()


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
        #terminal.show_new_plans(mps)
        mps.show_schedule()

        send_message_after_x_seconds = 1
        current_time = start_time = 0
        next_time = start_time + send_message_after_x_seconds
        send_current_day = True
        while current_time - start_time <= day_time:
            time.sleep(1) # current time is equal to 1s
            current_time += 1
            if current_time - start_time >= day_time:
                day_index += 1
                if day_index >= len(mps.get_plans_list()):
                    sys.exit(1)
                print(f"------------------------------------------------ day: {day_index} "
                      f"---------------------------------------")
                start_time = current_time = 0
                next_time = start_time + send_message_after_x_seconds
                pass_to_next_day()
                mps.show_schedule()
                send_current_day = True
                #mps.show_schedule()
                #terminal.show_new_plans(mps)
            elif send_current_day is True:
                next_time = current_time + send_message_after_x_seconds
                message = mps.get_plans_list()[0]
                comm_to_mes.set_msg(message)
                send_current_day = False
            elif comm_to_mes.get_feedback_msg() == FEEDBACK_MSG:
                comm_to_mes.set_msg(None)

        p.kill()
        sys.exit(1)
    except KeyboardInterrupt:
        terminal.exit(0, "Caught KeyboardInterrupt, terminating Terminal")
        print("Caught KeyboardInterrupt, terminating ERP")
        p.kill()
        # tcp_process.kill()
        sys.exit(1)
