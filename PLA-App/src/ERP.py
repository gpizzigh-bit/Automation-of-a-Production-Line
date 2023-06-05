import multiprocessing
import os
import sys
import threading
import time

from rich.traceback import install

from constants.local_constants import erp_to_mes_test_data

from modules import tcp_comm, MPS
from modules import udp_comm_class, terminal_class, database_orders_class

install(show_locals=True)

# TODO show the chosen supllier on the terminal

# Constants
UDP_IP = "0.0.0.0"  # local
UDP_PORT = 54321

TCP_IP = "127.0.0.1"  # local
TCP_PORT = 12345

FEEDBACK_MSG = "Message Received!"
HANDSHAKE_FROM_ERP = "HANDSHAKE FROM ERP"

day_time = 60

mps = MPS.Scheduler()
terminal = terminal_class.ErpTerminal()
day_index = 0


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


def calculate_cost_for_each_order(order):
    # stat_obj = database_orders_class.Statistics()
    # order_dic = dict(subString.split(":") for subString in order.split(";"))
    # order_number = order_dic[' number']
    # # TODO test function Delete after
    # Ad = 3  # <- MPS
    # Dd = 10  # <- MES
    # stat_obj.update_ad(order_number, Ad)
    # stat_obj.update_dc(order_number, )
    # print(order[' quantity'] * stat_obj.read_tc(order_dic[' number']))
    pass


def find_make_and_deliver(nested_list, target_workpiece):
    day_index = -1
    total_order_pieces = 0
    for i, inner_list in enumerate(nested_list):
        for d in inner_list:
            if d['status'] == 'store2deliver' and d['workpiece'] == target_workpiece:
                total_order_pieces += 1
            elif d['status'] == 'makeANDdeliver' and d['workpiece'] == target_workpiece:
                if day_index == -1:
                    day_index = i
                    for each_d in nested_list[day_index]:
                        if each_d['status'] == 'makeANDdeliver' and each_d['workpiece'] == target_workpiece:
                            total_order_pieces += 1
                    return day_index, total_order_pieces
    return day_index, total_order_pieces


def find_the_dispatch_day_of_each_order(nested_list):
    orders_obj = udp_comm_class.Orders()
    stat_obj = database_orders_class.Statistics()
    pending_orders = orders_obj.read_All_Orders()
    for order in pending_orders:
        order_dic = dict(subString.split(":") for subString in order.split(";"))
        # Gets the desired day to deliver the pieces of the order
        order_day_index, total_order_pieces = find_make_and_deliver(nested_list, order_dic[' workpiece'])
        print(f"{total_order_pieces} == {order_dic[' quantity']}")
        if total_order_pieces == order_dic[' quantity']:  # order found
            # send the dispatch day to the database
            stat_obj.update_dd(order_dic['number'], order_day_index)


def remove_whitespace(string):
    return ''.join(string.split())


def show_interface(day_index):
    days_ahead = 5

    print(f"------------------------------------------------ day: {day_index} "
          f"---------------------------------------------------")
    # Accept orders sent to it by its clients
    print(f"///////////// Pending orders /////////////")
    pending_orders_obj = database_orders_class.Orders()
    pending_orders = pending_orders_obj.read_All_Orders()
    for order in pending_orders[:days_ahead]:
        print(order)
    print()

    print(f"///////////// Concluded orders /////////////")
    concluded_orders_obj = database_orders_class.Concluded()
    orders = concluded_orders_obj.read_All_Concluded()
    for order in orders[:days_ahead]:
        print(order)
        # calculate_cost_for_each_order(order)
    print()

    print(f"///////////// Purchasing Plan /////////////")
    mps.show_day_ahead_purchasing_schedule(day_index, days_ahead)
    print()

    print(f"///////////// Factory Statistics /////////////")
    stats = database_orders_class.Statistics()
    for order in pending_orders[:days_ahead]:
        order_dic = dict(subString.split(":") for subString in order.split(";"))
        print(f"order number:{order_dic['number']} Total cost: {stats.get_order_total_cost(remove_whitespace(order_dic['number']))}")

    print(f"///////////// MPS {days_ahead}-days ahead /////////////")
    mps.show_day_ahead_schedule(day_index, days_ahead)
    print()
    print(
        f"-----------------------------------------------------------------------------------------------------------")


def simulate_day_cycle():
    comm_to_mes = ThreadedClient()
    comm_to_mes.start()
    day_index = 0
    mps.first_run()
    terminal.show_new_plans(mps)
    # mps.show_schedule()
    send_message_after_x_seconds = 1
    current_time = start_time = 0
    next_time = start_time + send_message_after_x_seconds
    send_current_day = True
    # initialize terminal
    # terminal.show_new_plans(mps)
    # terminal.run()
    while current_time - start_time <= day_time:
        time.sleep(1)  # current time is equal to 1s
        current_time += 1
        if current_time - start_time >= day_time:
            os.system('cls')
            day_index += 1
            # if day_index >= len(mps.get_plans_list()):
            #     sys.exit(1)  # this is just a security may halt the program
            show_interface(day_index)
            start_time = current_time = 0
            next_time = start_time + send_message_after_x_seconds
            pass_to_next_day()
            terminal.show_new_plans(mps)
            terminal.change_day(day_index)
            # mps.show_schedule()
            send_current_day = True
            # mps.show_schedule()
            # terminal.show_new_plans(mps)
        elif send_current_day is True:
            next_time = current_time + send_message_after_x_seconds
            message = mps.get_plans_list()[0]
            comm_to_mes.set_msg(message)
            send_current_day = False
        elif comm_to_mes.get_feedback_msg() == FEEDBACK_MSG:
            comm_to_mes.set_msg(None)


if __name__ == '__main__':
    terminal = terminal_class.ErpTerminal()
    p = multiprocessing.Process(target=process_orders)
    day_cycle = multiprocessing.Process(target=simulate_day_cycle)
    p.start()
    day_cycle.start()
    # terminal.run()
    # comm_to_mes = ThreadedClient()
    # comm_to_mes.start()
    # day_index = 0
    # try:
    #
    #     mps.first_run()
    #     terminal.show_new_plans(mps)
    #     print(f"Plan list: {mps.get_plans_list()}")
    #     #mps.show_schedule()
    #
    #     send_message_after_x_seconds = 1
    #     current_time = start_time = 0
    #     next_time = start_time + send_message_after_x_seconds
    #     send_current_day = True
    #     # initialize terminal
    #     terminal.show_new_plans(mps)
    #     #terminal.run()
    #     t.start()
    #     while current_time - start_time <= day_time:
    #         time.sleep(1) # current time is equal to 1s
    #         current_time += 1
    #         if current_time - start_time >= day_time:
    #             day_index += 1
    #             if day_index >= len(mps.get_plans_list()):
    #                 sys.exit(1)
    #             # print(f"------------------------------------------------ day: {day_index} "
    #             #       f"---------------------------------------")
    #             start_time = current_time = 0
    #             next_time = start_time + send_message_after_x_seconds
    #             pass_to_next_day()
    #             terminal.show_new_plans(mps)
    #             terminal.change_erp_day(day_index)
    #             #mps.show_schedule()
    #             send_current_day = True
    #             #mps.show_schedule()
    #             #terminal.show_new_plans(mps)
    #         elif send_current_day is True:
    #             next_time = current_time + send_message_after_x_seconds
    #             message = mps.get_plans_list()[0]
    #             comm_to_mes.set_msg(message)
    #             send_current_day = False
    #         elif comm_to_mes.get_feedback_msg() == FEEDBACK_MSG:
    #             comm_to_mes.set_msg(None)

    # day_cycle.kill()
    # p.kill()
    # sys.exit(1)
    # except KeyboardInterrupt:
    #     terminal.exit(0, "Caught KeyboardInterrupt, terminating Terminal")
    #     print("Caught KeyboardInterrupt, terminating ERP")
    #     p.kill()
    #     # tcp_process.kill()
    #     sys.exit(1)
