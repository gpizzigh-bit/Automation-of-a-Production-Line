"""
simple FIFO planner for the MPS scheduler, we must try to reach each deadline
made by: Gabriel Pizzighini Salvador (gpizzigh-bit)
"""

import math

from .database_orders_class import Orders, Stock

# from ..constants import local_constants

STORE_GLOBAL = "makeANDstore"
DELIVER_GLOBAL = "makeANDdeliver"
STORE2DELIVER = "store2deliver"
STORE2DELIVER_WAREHOUSE_LIMIT = 17  # 17
LIMIT_OF_DELIVER_BY_DAY = 5
RESTOCK_THRESHOLD = {"P1": 10, "P2": 20}
P1_RESTOCK_LIMIT_BY_DAY = 2  # pieces
P2_RESTOCK_LIMIT_BY_DAY = 5  # pieces

from constants.local_constants import suppliers


# TODO update the piece count as the db is not working still


def request_piece(workpiece, status):
    return {"workpiece": workpiece, "status": status}


def get_manufacturing_days(order_type):
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


def find_in_tree(origin_type, piece_type):
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


def check_for_decimal_to_add_one(num):
    if math.floor(num) != num:
        return math.ceil(num)
    else:
        return num


def contains_only_dict(request):
    if not request:  # check if list is empty
        return False
    for elem in request:
        if not isinstance(elem, dict):  # check if element is not a dictionary
            return False
    return True


def find_supplier(piece_type: str, quantity: int, delivery_time: int):
    # Filter out suppliers that can't meet the delivery time or minimum order quantity
    valid_suppliers = {supplier: info for supplier, info in suppliers.items() if
                       info[piece_type]['delivery_time'] <= delivery_time and info[piece_type][
                           'min_order_quantity'] <= quantity}

    # Find the supplier with the lowest cost per piece
    best_supplier = min(valid_suppliers, key=lambda x: valid_suppliers[x][piece_type]['price'])

    return best_supplier


def restock_shift_list(nested_list, index, quantity, day_objective):
    for i in range(quantity):
        nested_list.insert(index + i, [day_objective])
    return nested_list


def add_one_if_float(num):
    if isinstance(num, float) and num != int(num):
        return int(num + 1)
    else:
        return num


class Scheduler:

    def __init__(self):
        self.count_execution = 0
        self.current_day = None
        self.order_dic = None
        self.order_list = []
        self.nested_result_list = []
        self.total_time = 0
        self.deadline = 1
        self.totalmachines = 4
        self.total_p1_piece_count = 0
        self.total_p2_piece_count = 0
        self.request_lock_current_day = False
        self.p1_supplier = None
        self.p2_supplier = None

    def run(self):
        print("Starting Scheduler", end='')
        if self.request_lock_current_day:
            self.count_execution += 1
            # run the algorithm without considering the first day
            self.nested_result_list = []
            self.order_list = []
            # TODO don't connect to the database inside the mps this is slowing down execution
            self._parse_data()
            print(".", end='')
            self.find_last_deadline()
            print(".", end='')
            self.find_total_time()
            print(".", end='')
            self.total_p1_piece_count = 0
            self.total_p2_piece_count = 0

            for order_number in range(0, len(self.order_list)):
                if order_number != 0:
                    print(".", end='')
                    self.schedule_order(order_number)

            self.resolve_all_conflicts()
            print(".", end='')

            if self.count_stored2deliver_pieces() >= STORE2DELIVER_WAREHOUSE_LIMIT:  # 4
                # Request a day to only deliver stored ready pieces
                self.request_delivery_day()
                print(".", end='')

            self.check_warehouse_status()
            print(".", end='')

            self.lock_current_day()
            print(".", end='')
            self.request_lock_current_day = False
            print("Done")

            return self.nested_result_list

    def first_run(self):
        print("Starting Scheduler", end='')
        self.nested_result_list = []
        self.order_list = []
        # TODO don't connect to the database inside the mps this is slowing down execution
        self._parse_data()
        print(".", end='')
        self.find_last_deadline()
        print(".", end='')
        self.find_total_time()
        print(".", end='')

        for order_number in range(0, len(self.order_list)):
            # for order_number in range(0, 3):
            print(".", end='')
            self.schedule_order(order_number)

        self.resolve_all_conflicts()
        print(".", end='')

        if self.count_stored2deliver_pieces() >= STORE2DELIVER_WAREHOUSE_LIMIT:  # 4
            # Request a day to only deliver stored ready pieces
            print(".", end='')
            self.request_delivery_day()

        self.check_warehouse_status()
        print(".", end='')
        print("Done")

        return self.nested_result_list

    def _parse_data(self):
        # get the pending orders form the database
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

    def update_the_total_piece_count(self, order_type, total):
        warehouse = Stock()
        match order_type:
            case "P6" | "P8":
                self.total_p1_piece_count += total
                # warehouse.update_Stock_P1(self.total_p1_piece_count)
            case "P4" | "P7" | "P9" | "P5" | "P3":
                self.total_p2_piece_count += total
                # warehouse.update_Stock_P2(self.total_p2_piece_count)

    def schedule_order(self, order_pos_in_list):
        # check the order quantity, type, duedate
        order_type = self.order_list[order_pos_in_list][' workpiece'].replace(" ", "")
        order_total_size = int(self.order_list[order_pos_in_list][' quantity'])
        self.update_the_total_piece_count(order_type, order_total_size)
        order_deadline = int(self.order_list[order_pos_in_list][' duedate'])

        manufacturing_days = get_manufacturing_days(order_type)

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
        piece_tree = find_in_tree("P2", order_type)
        # arrange them based on the deadline
        aux = -1
        store_local = STORE_GLOBAL
        for days in range(0, total_days):
            if days != 0:
                # self.nested_result_list[order_deadline - days].append(self.request_piece(order_type, "make"))
                for _ in range(0, int(order_total_size / (total_days / manufacturing_days))):
                    self.nested_result_list[order_deadline - days].append(
                        request_piece(piece_tree[aux], store_local))
                if days == manufacturing_days - 1:
                    aux = 0  # reset index
                    # here we need to signal to store and deliver the piece
                    store_local = STORE2DELIVER
                else:
                    store_local = STORE_GLOBAL
                aux -= 1
            else:
                # self.nested_result_list[order_deadline - days].append(self.request_piece(order_type, "make&deliver"))
                for _ in range(0, int(order_total_size / (total_days / manufacturing_days))):
                    self.nested_result_list[order_deadline - days].append(
                        request_piece(piece_tree[aux], DELIVER_GLOBAL))
                aux -= 1

        # remove the time consumed
        self.total_time -= time_to_complete

        # TODO - send to database

    def check_for_conflicts(self):
        for day_list in self.nested_result_list:
            if len(day_list) > 4:
                return True
        return False

    def resolve_all_conflicts(self):
        pos_in_loop = 0
        size_of_nested_list = len(self.nested_result_list)
        # identify conflicts
        while self.check_for_conflicts():
            pos_in_nested_list = 0
            for day_list in self.nested_result_list:
                if len(day_list) > 4 and contains_only_dict(day_list):
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

    def count_stored2deliver_pieces(self):
        total = 0
        for requestPiece in self.nested_result_list:
            if contains_only_dict(requestPiece):
                for index in range(0, len(requestPiece)):
                    if requestPiece[index]['status'] == STORE2DELIVER:
                        total += 1
        return total

    def request_delivery_day(self):
        # calculate total delivery needed days
        total_days2deliver = check_for_decimal_to_add_one(STORE2DELIVER_WAREHOUSE_LIMIT / LIMIT_OF_DELIVER_BY_DAY)
        # move all requests forward
        self.shift_nested_list(total_days2deliver, "delivery day")

    def shift_nested_list(self, number_of_days, msg):
        if not isinstance(self.nested_result_list, list):
            return
        number_of_days = int(number_of_days)
        num_positions = number_of_days
        result = [[msg] for _ in range(num_positions)] + self.nested_result_list
        for i in range(len(result)):
            if i < num_positions:
                continue
            result[i] = result[i][-number_of_days:] + result[i][:-number_of_days]
        self.nested_result_list = result

    def check_warehouse_status(self):
        # connect to the database of the warehouse
        warehouse = Stock()
        amount_of_p1 = warehouse.read_Stock_P1()
        amount_of_p2 = warehouse.read_Stock_P2()
        # compare to the total requested by the pending orders
        if amount_of_p1 <= RESTOCK_THRESHOLD["P1"] and amount_of_p2 <= RESTOCK_THRESHOLD["P2"]:
            # if bellow limit of the threshold request a restocking day
            # calculate number of days to restock
            needed_days = (RESTOCK_THRESHOLD["P1"] - amount_of_p1) / P1_RESTOCK_LIMIT_BY_DAY + (
                    RESTOCK_THRESHOLD["P2"] - amount_of_p2) / P2_RESTOCK_LIMIT_BY_DAY

            needed_days = add_one_if_float(needed_days)  # add one day of not int
            # find a supplier for the difference of the needed pieces to reach the threshold
            self.p1_supplier = find_supplier("P1", (RESTOCK_THRESHOLD["P1"] - amount_of_p1), needed_days)
            self.p2_supplier = find_supplier("P2", (RESTOCK_THRESHOLD["P2"] - amount_of_p2), needed_days)

            desired_index_day = needed_days * max(suppliers[self.p1_supplier]['P1']['delivery_time'],
                                                  suppliers[self.p2_supplier]['P1']['delivery_time'])
            restock_shift_list(self.nested_result_list, desired_index_day, needed_days, request_piece("P1 and P2 restock", ''))

        elif amount_of_p1 <= RESTOCK_THRESHOLD["P1"]:
            needed_days = (RESTOCK_THRESHOLD["P1"] - amount_of_p1) / P1_RESTOCK_LIMIT_BY_DAY
            needed_days = add_one_if_float(needed_days)  # add one day of not int
            self.p1_supplier = find_supplier("P1", RESTOCK_THRESHOLD["P1"] - amount_of_p1, needed_days)
            desired_index_day = needed_days * suppliers[self.p1_supplier]['P1']['delivery_time']
            restock_shift_list(self.nested_result_list, desired_index_day, needed_days, request_piece("P1 restock", ''))

        # now for piece p2
        elif amount_of_p2 <= RESTOCK_THRESHOLD["P2"]:
            needed_days = (RESTOCK_THRESHOLD["P2"] - amount_of_p2) / P2_RESTOCK_LIMIT_BY_DAY
            needed_days = add_one_if_float(needed_days)  # add one day of not int
            self.p2_supplier = find_supplier("P2", RESTOCK_THRESHOLD["P2"] - amount_of_p2, needed_days)
            desired_index_day = needed_days * suppliers[self.p2_supplier]['P1']['delivery_time']
            restock_shift_list(self.nested_result_list, desired_index_day, needed_days, request_piece("P2 restock", ''))

    def lock_current_day(self):
        # copy the current day on a self list
        self.current_day = self.nested_result_list[0].copy()
        # self.nested_result_list.pop(0)
        for _ in range(0, self.count_execution):
            del self.nested_result_list[0]
        print("deleted current day")
        # for i in range(len(self.nested_result_list)):
        #     self.nested_result_list[i+1] = self.nested_result_list[i+1][:]

    def show_schedule(self):
        day = 0
        for each_list in self.nested_result_list[:4]:
            print(f"day:{day} \n {each_list}")
            day += 1

    def get_plans_list(self):
        return self.nested_result_list

    def get_suppliers(self):
        return self.p1_supplier, self.p2_supplier
