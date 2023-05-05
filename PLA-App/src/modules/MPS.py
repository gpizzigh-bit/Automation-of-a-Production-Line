# [TODO] Calaculate the work-piece amount per day
# [TODO] Calculate used capacity on a day


"""
simple FIFO planner for the MPS scheduler, we must try to reach each deadline

"""

from .database_orders_class import Database, Orders


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
        manufacturing_days = 0
        self._parse_data()
        self.find_last_deadline()
        self.find_total_time()

        # there is a maximum of pieces that can be manufactured by day these are represented by tokens
        # aim at the first orders deadline

        # # check the first orders quantity
        # first_order_type = self.order_list[0][' workpiece'].replace(" ", "")
        # first_order_total_size = int(self.order_list[0][' quantity'])
        # first_order_deadline = int(self.order_list[0][' duedate'])
        # match first_order_type:
        #     case "P9":
        #         manufacturing_days = 3
        #
        # if first_order_total_size >= self.totalmachines:
        #     # order takes more than 1 day to make need to subdivide
        #     fullbooked_days = manufacturing_days * int(first_order_total_size / self.totalmachines)
        #     if first_order_total_size % self.totalmachines != 0:
        #         extradays = self.totalmachines - first_order_total_size % self.totalmachines
        #     else:
        #         extradays = 0
        #     total_days = fullbooked_days + extradays
        #     time_to_complete = total_days * 60
        #
        # # arrange them based on the deadline
        # for days in range(0, total_days):
        #     if days != 0:
        #         self.result_list[first_order_deadline - days] = [self.request_piece("P9", "make")]
        #     else:
        #         self.result_list[first_order_deadline - days] = [self.request_piece("P9", "make&deliver")]
        # # remove the time consumed
        # self.total_time -= time_to_complete

        self.schedule_order(0)
        self.schedule_order(1)

        print(self.nested_result_list)

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
            total_days = 1
            time_to_complete = total_days * 60

        # arrange them based on the deadline
        for days in range(0, total_days):
            if days != 0:
                self.nested_result_list[order_deadline - days].append(self.request_piece(order_type, "make"))
            else:
                self.nested_result_list[order_deadline - days].append(self.request_piece(order_type, "make&deliver"))

        # remove the time consumed
        self.total_time -= time_to_complete

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


