# [TODO] Calaculate the work-piece amount per day
# [TODO] Calculate used capacity on a day


"""
simple FIFO planner for the MPS scheduler, we must try to reach each deadline

"""

from .database_orders_class import Database, Orders
import numpy as np

STORE_GLOBAL = "makeANDstore"
DELIVER_GLOBAL = "makeANDdeliver"


class Scheduler:

    def __init__(self):
        self.order_dic = None
        self.order_list = []
        # self.result_list = []
        self.nested_result_list = []
        self.total_time = 0
        self.deadline = 1
        self.totalmachines = 4

    def run(self):

        # TODO don't connect to teh database inside the mps this is slowing down execution
        self._parse_data()
        self.find_last_deadline()
        self.find_total_time()

        # for each_order in self.order_list:
        #     print(each_order)

        for order_number in range(0, len(self.order_list)):
            # for order_number in range(0, 3):
            self.schedule_order(order_number)

        self.resolve_all_conflicts()

        day = 0
        for each_list in self.nested_result_list:
            print(f"day:{day} \n {each_list}")
            day += 1

        return self.nested_result_list

    def _parse_data(self):
        # get the pending orders form the database
        db = Database()
        pending_orders_obj = Orders()
        pending_orders = pending_orders_obj.read_All_Orders()
        for order in pending_orders[1:]:
            self.order_dic = dict(subString.split(":") for subString in order.split(";"))
            self.order_list.append(self.order_dic)

    def find_last_deadline(self):
        for _ in range(0, len(self.order_list) - 1):
            aux_deadline = int(self.order_list[_][' duedate'])
            if aux_deadline > self.deadline:
                self.deadline = aux_deadline  # found the biggest deadline

        for _ in range(0, self.deadline + 1):
            self.nested_result_list.append(list())

    def find_total_time(self):
        self.total_time = 60 * self.deadline
        pass

    def request_piece(self, workpiece, status):
        return {"worpiece": workpiece, "status": status}

    def schedule_order(self, order_pos_in_list):
        # check the order quantity, type, duedate
        order_type = self.order_list[order_pos_in_list][' workpiece'].replace(" ", "")
        order_total_size = int(self.order_list[order_pos_in_list][' quantity'])
        order_deadline = int(self.order_list[order_pos_in_list][' duedate'])

        manufacturing_days = self.get_manufacturing_days(order_type)

        if order_total_size >= self.totalmachines:
            # order takes more than 1 day to make need to subdivide
            fullbooked_days = manufacturing_days * int(order_total_size / self.totalmachines)

            if order_total_size % self.totalmachines != 0:
                extradays = self.totalmachines - order_total_size % self.totalmachines
            else:
                extradays = 0

            total_days = fullbooked_days + extradays
            time_to_complete = total_days * 60
        else:
            total_days = manufacturing_days
            time_to_complete = total_days * 60

        # TODO check for storage capacity
        piece_tree = self.find_in_tree("P2", order_type)
        # arrange them based on the deadline
        aux = -1
        store_local = STORE_GLOBAL
        for days in range(0, total_days):
            if days != 0:
                # self.nested_result_list[order_deadline - days].append(self.request_piece(order_type, "make"))
                for _ in range(0, int(order_total_size / (total_days / manufacturing_days))):
                    self.nested_result_list[order_deadline - days].append(
                        self.request_piece(piece_tree[aux], store_local))
                if days == manufacturing_days - 1:
                    aux = 0  # reset index
                    # here we need to signal to store and deliver the piece
                    store_local = "storeANDdeliver"
                else:
                    store_local = STORE_GLOBAL
                aux -= 1
            else:
                # self.nested_result_list[order_deadline - days].append(self.request_piece(order_type, "make&deliver"))
                for _ in range(0, int(order_total_size / (total_days / manufacturing_days))):
                    self.nested_result_list[order_deadline - days].append(
                        self.request_piece(piece_tree[aux], DELIVER_GLOBAL))
                aux -= 1

        # remove the time consumed
        self.total_time -= time_to_complete

        # TODO - create piece orders on the MPS
        # TODO - Show desired 4 pieces per day
        # TODO - resolve conflicts if more than 4 piece per day
        # TODO - send to database

    def get_manufacturing_days(self, order_type):
        order_type = order_type.replace(" ", "")
        match order_type:
            case "P4" | "P3" | "P6":
                return 1
            case "P7":
                return 2
            case "P9" | "P8":
                return 3
            case "P5":
                return 4

    def find_in_tree(self, origin_type, piece_type):
        result_list = []
        match piece_type:
            case "P4":
                result_list.extend(["P4"])
                return result_list
            case "P7":
                result_list.extend(["P4", "P7"])
                return result_list
            case "P9":
                result_list.extend(["P4", "P7", "P9"])
                return result_list
            case "P5":
                result_list.extend(["P4", "P7", "P9", "P5"])
                return result_list
            case "P6":
                if origin_type == "P2":
                    result_list.extend(["P3", "P6"])
                    return result_list
                elif origin_type == "P1":
                    result_list.extend(["P6"])
                    return result_list
            case "P3":
                result_list.extend(["P3"])
                return result_list
            case "P8":
                if origin_type == "P2":
                    result_list.extend(["P3", "P6", "P8"])
                    return result_list
                elif origin_type == "P1":
                    result_list.extend(["P6", "P8"])
                    return result_list

    def check_for_conflicts(self):
        for day_list in self.nested_result_list:
            if len(day_list) > 4:
                return True
        return False

    def resolve_all_conflicts(self):
        pos_in_loop = 0
        size_of_nested_list = len(self.nested_result_list)
        # identify conflicts
        #while pos_in_loop <= size_of_nested_list:
        while self.check_for_conflicts():
            pos_in_nested_list = 0
            for day_list in self.nested_result_list:
                if len(day_list) > 4:
                    # check pieces penalties, because we are doing a FIFO we move the last piece forward
                    # make a decision
                    # resolve them somehow
                    # move pieces
                    # update the nested list
                    if (pos_in_nested_list + 1) >= len(self.nested_result_list):
                        self.nested_result_list.append(list())
                        size_of_nested_list = len(self.nested_result_list)
                    self.nested_result_list[pos_in_nested_list + 1].append(day_list[-1])
                    day_list.pop()  # removes the last element
                pos_in_nested_list += 1
            pos_in_loop += 1
