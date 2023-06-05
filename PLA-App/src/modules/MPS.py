"""
simple FIFO planner for the MPS scheduler, we must try to reach each deadline
made by: Gabriel Pizzighini Salvador (gpizzigh-bit)
"""

import math
import time

from .database_orders_class import Orders, Stock, Statistics

from constants.local_constants import *


def request_piece(workpiece, status):
    return {"workpiece": workpiece, "status": status, "p1_amount": 0, "p2_amount": 0}


def request_piece_with_tag(workpiece, status, order_number):
    return {"workpiece": workpiece, "status": status, "p1_amount": 0, "p2_amount": 0, "order_id": order_number}


def request_restock(workpiece, status, p1_amount, p2_amount):
    return {"workpiece": workpiece, "status": status, "p1_amount": p1_amount, "p2_amount": p2_amount}


def get_manufacturing_days(order_type):
    order_type = order_type.replace(" ", "")
    match order_type:
        case "P4" | "P3":
            return 1
        case "P7":
            return 2
        case "P9":
            return 3
        case "P5":
            return 4
        case "P6":
            return 1
        case "P8":
            return 2


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

    if valid_suppliers is None:
        return supplier['C']

    # Find the supplier with the lowest cost per piece
    best_supplier = min(valid_suppliers, key=lambda x: valid_suppliers[x][piece_type]['price'])

    return best_supplier


def restock_shift_list(nested_list, index, quantity, day_objective):
    for i in range(add_one_if_float(quantity)):
        nested_list.insert(index + i, [day_objective])
    return nested_list


def add_one_if_float(num):
    if isinstance(num, float) and num != int(num):
        return int(num + 1)
    else:
        return int(num)


def count_empty_days(nested_list):
    count = 0
    for inner_list in nested_list:
        if not inner_list:
            count += 1
        else:
            break
    return count


def create_empty_nested_list(nested_list):
    result = []
    for inner_list in nested_list:
        result.append([])
    return result


def has_different_element(lst1, lst2):
    return not set(lst1).issubset(set(lst2))


def find_if_p1_or_p2(desired_piece):
    if desired_piece in ["P3", "P4", "P7", "P9", "P5"]:
        return "P2"
    else:
        return "P1"


def update_all_orders_arrival_day(arraival_day):
    orders_obj = Orders()
    statistics = Statistics()
    orders = orders_obj.read_All_Orders()
    for order in orders:
        order_dic = dict(subString.split(":") for subString in order.split(";"))
        statistics.update_ad(order_dic['number'], arraival_day)


# def find_make_and_deliver(nested_list, target_workpiece):
#     day_index = -1
#     total_order_pieces = 0
#     for i, inner_list in enumerate(nested_list):
#         for d in inner_list:
#             if d['status'] == 'store2deliver' and d['workpiece'] == target_workpiece:
#                 total_order_pieces += 1
#             elif d['status'] == 'makeANDdeliver' and d['workpiece'] == target_workpiece:
#                 if day_index == -1:
#                     day_index = i
#                     for each_d in nested_list[day_index]:
#                         if each_d['status'] == 'makeANDdeliver' and each_d['workpiece'] == target_workpiece:
#                             total_order_pieces += 1
#                     return day_index, total_order_pieces
#     return day_index, total_order_pieces
#
# def find_the_dispatch_day_of_each_order(nested_list):
#     orders_obj = Orders()
#     result = []


class Scheduler:

    def __init__(self):
        self.amount_of_p2_to_restock = None
        self.amount_of_p1_to_restock = None
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
        self.nested_purchasing_list = []

    def run(self):
        if self.request_lock_current_day:
            self.count_execution += 1
            # run the algorithm without considering the first day
            self.nested_result_list = []
            self.order_list = []
            self._parse_data()
            self.find_last_deadline()
            self.find_total_time()
            self.total_p1_piece_count = 0
            self.total_p2_piece_count = 0
            for order_number in range(0, len(self.order_list)):
                if order_number != 0:
                    self.schedule_order(order_number)
            self.resolve_all_conflicts()
            # if self.count_stored2deliver_pieces() >= STORE2DELIVER_WAREHOUSE_LIMIT:  # 4
            #     # Request a day to only deliver stored ready pieces
            #     self.request_delivery_day()
            self.check_warehouse_status()
            self.lock_current_day()
            self.request_lock_current_day = False

            return self.nested_result_list

    def first_run(self):
        print("Starting Scheduler.", end='')
        statistics_obj = Statistics()
        print(".", end='')
        self.nested_result_list = []
        self.order_list = []
        self._parse_data()
        print(".", end='')
        self.find_last_deadline()
        print(".", end='')
        self.find_total_time()
        print(".", end='')
        for order_number in range(0, len(self.order_list)):
            statistics_obj.delete_statistics_row(self.order_list[order_number]['number'])
            statistics_obj.add_statistics_Row(self.order_list[order_number]['number'], 0.00, 0.00, 0.00, 0.00, 0.00,
                                              0.00)
            self.schedule_order(order_number)
            print(".", end='')

        self.resolve_all_conflicts()
        print(".", end='')
        # if self.count_stored2deliver_pieces() >= STORE2DELIVER_WAREHOUSE_LIMIT:  # 4
        #     # Request a day to only deliver stored ready pieces
        #     self.request_delivery_day()
        #     print(".", end='')
        self.check_warehouse_status()
        print(".Done")

        return self.nested_result_list

    def _parse_data(self):
        # get the pending orders form the database
        pending_orders_obj = Orders()
        pending_orders = pending_orders_obj.read_All_Orders()
        if len(pending_orders) == 0:
            print("Waiting for new orders", end='')
        while True:
            pending_orders = pending_orders_obj.read_All_Orders()  # update the pending orders
            if len(pending_orders) != 0:
                for order in pending_orders:
                    self.order_dic = dict(subString.split(":") for subString in order.split(";"))
                    self.order_list.append(self.order_dic)
                break
            else:
                print(".", end='')
                time.sleep(1)

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
        order_number = self.order_list[order_pos_in_list]['number']
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

        if order_type in ['P4', 'P7', 'P9', 'P5', 'P3']:
            piece_tree = find_in_tree("P2", order_type)
        elif order_type in ['P6', 'P8']:
            piece_tree = find_in_tree("P1", order_type)
        # arrange them based on the deadline
        aux = -1
        store_local = STORE_GLOBAL
        for days in range(0, total_days):
            if days != 0:
                # self.nested_result_list[order_deadline - days].append(self.request_piece(order_type, "make"))
                for _ in range(0, int(order_total_size / (total_days / manufacturing_days))):
                    if len(piece_tree) == 1:
                        self.nested_result_list[order_deadline - days].append(
                            request_piece(piece_tree[0], store_local))
                    else:
                        self.nested_result_list[order_deadline - days].append(
                            request_piece(piece_tree[aux], store_local))

                    if store_local == STORE2DELIVER:
                        self.nested_result_list[order_deadline - days].append(
                            request_piece_with_tag(piece_tree[aux], store_local, order_number))
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
                        request_piece_with_tag(piece_tree[aux], DELIVER_GLOBAL, order_number))
                aux -= 1

        # remove the time consumed
        self.total_time -= time_to_complete

        # # TODO - send to database
        # stat = Statistics()
        # stat.update_dd(order_number, int(total_days))

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
        self.nested_purchasing_list = create_empty_nested_list(self.nested_result_list)

        if amount_of_p1 == 0 and amount_of_p2 == 0:
            # Fresh factory status
            # count available days before firsts order
            needed_days = count_empty_days(self.nested_result_list)
            self.amount_of_p1_to_restock = (RESTOCK_THRESHOLD["P1"] - amount_of_p1)
            self.amount_of_p2_to_restock = (RESTOCK_THRESHOLD["P2"] - amount_of_p2)
            self.p1_supplier = find_supplier("P1", (RESTOCK_THRESHOLD["P1"] - amount_of_p1), needed_days)
            self.p2_supplier = find_supplier("P2", (RESTOCK_THRESHOLD["P2"] - amount_of_p2), needed_days)
            self.total_cost_of_p1 = self.amount_of_p1_to_restock * suppliers[self.p1_supplier]['P1']['price']
            self.total_cost_of_p2 = self.amount_of_p2_to_restock * suppliers[self.p2_supplier]['P2']['price']

            self.nested_purchasing_list[suppliers[self.p1_supplier]['P1']['delivery_time']].append()

            total_index = 0
            for index in range(0, needed_days - 1):
                self.nested_result_list[index] = request_restock(P1_AND_P2_RESTOCK_STR, '0',
                                                                 self.amount_of_p1_to_restock,
                                                                 self.amount_of_p2_to_restock)
                total_index += 1

            # update_all_orders_arrival_day(total_index)

            self.nested_purchasing_list[total_index - suppliers[self.p1_supplier]['P1']['delivery_time']].append(
                f"Buy from {self.p1_supplier} {self.amount_of_p1_to_restock} P1s")

            self.nested_purchasing_list[total_index - suppliers[self.p2_supplier]['P2']['delivery_time']].append(
                f"Buy form {self.p2_supplier} {self.amount_of_p2_to_restock} P2s")

            # restock_shift_list(self.nested_result_list, 0, needed_days,
            #                    request_piece("P1 and P2 restock", ''))
        """if amount_of_p2 == 0:
            needed_days = count_empty_days(self.nested_result_list)
            self.p2_supplier = find_supplier("P2", (RESTOCK_THRESHOLD["P2"]), needed_days)
            self.total_cost_of_p2 = self.amount_of_p2_to_restock * suppliers[self.p2_supplier]['P2']['price']
            self.nested_purchasing_list[suppliers[self.p1_supplier]['P1']['delivery_time']].append()
            desired_index_day = needed_days * suppliers[self.p2_supplier]['P2']['delivery_time']
            restock_shift_list(self.nested_result_list, desired_index_day, needed_days,
                               request_restock(P2_RESTOCK_STR, '0', 0, self.amount_of_p2_to_restock))

            # need to implement for these cases too
            self.nested_purchasing_list[
                desired_index_day - suppliers[self.p2_supplier]['P2']['delivery_time']].append(
                f"Buy form {self.p2_supplier} {self.amount_of_p2_to_restock} P2s")"""

        # compare to the total requested by the pending orders
        if amount_of_p1 < RESTOCK_THRESHOLD["P1"] and amount_of_p2 < RESTOCK_THRESHOLD["P2"]:
            # if bellow limit of the threshold request a restocking day
            # calculate number of days to restock
            needed_days = (RESTOCK_THRESHOLD["P1"] - amount_of_p1) / P1_RESTOCK_LIMIT_BY_DAY + \
                          (RESTOCK_THRESHOLD["P2"] - amount_of_p2) / P2_RESTOCK_LIMIT_BY_DAY

            needed_days = add_one_if_float(needed_days)  # add one day of not int
            self.amount_of_p1_to_restock = (RESTOCK_THRESHOLD["P1"] - amount_of_p1)
            self.amount_of_p2_to_restock = (RESTOCK_THRESHOLD["P2"] - amount_of_p2)
            # find a supplier for the difference of the needed pieces to reach the threshold
            self.p1_supplier = find_supplier("P1", (RESTOCK_THRESHOLD["P1"] - amount_of_p1), needed_days)
            self.p2_supplier = find_supplier("P2", (RESTOCK_THRESHOLD["P2"] - amount_of_p2), needed_days)

            self.total_cost_of_p1 = self.amount_of_p1_to_restock * suppliers[self.p1_supplier]['P1']['price']
            self.total_cost_of_p2 = self.amount_of_p2_to_restock * suppliers[self.p2_supplier]['P2']['price']
            desired__p1_index_day = needed_days * suppliers[self.p1_supplier]['P1']['delivery_time']
            desired__p2_index_day = needed_days * suppliers[self.p2_supplier]['P2']['delivery_time']
            desired_index_day = needed_days * max(suppliers[self.p1_supplier]['P1']['delivery_time'],
                                                  suppliers[self.p2_supplier]['P2']['delivery_time'])

            # update_all_orders_arrival_day(desired_index_day)

            self.nested_purchasing_list[
                desired__p1_index_day - suppliers[self.p1_supplier]['P1']['delivery_time']].append(
                f"Buy from {self.p1_supplier} {self.amount_of_p1_to_restock} P1s")

            self.nested_purchasing_list[
                desired__p2_index_day - suppliers[self.p2_supplier]['P2']['delivery_time']].append(
                f"Buy form {self.p2_supplier} {self.amount_of_p2_to_restock} P2s")

            restock_shift_list(self.nested_result_list, desired_index_day, needed_days,
                               request_restock(P1_AND_P2_RESTOCK_STR, '0', self.amount_of_p1_to_restock,
                                               self.amount_of_p2_to_restock))

        elif amount_of_p1 < RESTOCK_THRESHOLD["P1"]:
            needed_days = (RESTOCK_THRESHOLD["P1"] - amount_of_p1) / P1_RESTOCK_LIMIT_BY_DAY
            needed_days = add_one_if_float(needed_days)  # add one day of not int
            self.amount_of_p1_to_restock = (RESTOCK_THRESHOLD["P1"] - amount_of_p1)
            self.p1_supplier = find_supplier("P1", RESTOCK_THRESHOLD["P1"] - amount_of_p1, needed_days)
            self.total_cost_of_p1 = self.amount_of_p1_to_restock * suppliers[self.p1_supplier]['P1']['price']
            desired_index_day = needed_days * suppliers[self.p1_supplier]['P1']['delivery_time']
            restock_shift_list(self.nested_result_list, desired_index_day, needed_days,
                               request_restock(P1_RESTOCK_STR, '0', self.amount_of_p1_to_restock, 0))
            self.nested_purchasing_list[
                desired_index_day - suppliers[self.p1_supplier]['P1']['delivery_time']].append(
                f"Buy from {self.p1_supplier} {self.amount_of_p1_to_restock} P1s")

            # need to implement for these cases too

        # now for piece p2
        elif amount_of_p2 < RESTOCK_THRESHOLD["P2"]:
            needed_days = (RESTOCK_THRESHOLD["P2"] - amount_of_p2) / P2_RESTOCK_LIMIT_BY_DAY
            needed_days = add_one_if_float(needed_days)  # add one day of not int
            self.amount_of_p2_to_restock = (RESTOCK_THRESHOLD["P2"] - amount_of_p2)
            self.p2_supplier = find_supplier("P2", RESTOCK_THRESHOLD["P2"] - amount_of_p2, needed_days)
            self.total_cost_of_p2 = self.amount_of_p2_to_restock * suppliers[self.p2_supplier]['P2']['price']
            desired_index_day = needed_days * suppliers[self.p2_supplier]['P2']['delivery_time']
            restock_shift_list(self.nested_result_list, desired_index_day, needed_days,
                               request_restock(P2_RESTOCK_STR, '0', 0, self.amount_of_p2_to_restock))

            # need to implement for these cases too

            self.nested_purchasing_list[
                desired_index_day - suppliers[self.p2_supplier]['P2']['delivery_time']].append(
                f"Buy form {self.p2_supplier} {self.amount_of_p2_to_restock} P2s")

    def lock_current_day(self):
        # copy the current day on a self list
        self.current_day = self.nested_result_list[0].copy()
        for _ in range(0, self.count_execution):
            del self.nested_result_list[0]
            del self.nested_purchasing_list[0]

    def show_schedule(self):
        day = 0
        for each_list in self.nested_result_list[:10]:
            print(f"day:{day} \n {each_list}")
            day += 1

    def show_day_ahead_purchasing_schedule(self, day_index, days_ahead):
        day = day_index
        for buy_order in self.nested_purchasing_list[:days_ahead]:
            print(f"day: {day} -> {buy_order}")
            day += 1

    def show_day_ahead_schedule(self, day_index, days_ahead):
        day = day_index
        for order in self.nested_result_list[:days_ahead]:
            if not not order:
                # if not empty
                if order[0]['workpiece'] == P1_AND_P2_RESTOCK_STR:
                    print(f"day: {day} ->" f" RESTOCK with suppliers {self.get_suppliers()[0]} for"
                          f" P1 and {self.get_suppliers()[1]} for P2 for a total of {self.total_cost_of_p1 + self.total_cost_of_p2}€ ")
                    day += 1
                elif order[0]['workpiece'] == P1_RESTOCK_STR:
                    print(f"day: {day} ->" f" RESTOCK with suppliers {self.get_suppliers()[0]} "
                          f"for P1 for a total of {self.total_cost_of_p1}€ ")
                    day += 1
                elif order[0]['workpiece'] == P2_RESTOCK_STR:
                    print(f"day: {day} ->"f" RESTOCK with suppliers {self.get_suppliers()[1]} "
                          f"for P2 for a total of {self.total_cost_of_p2}€ ")
                    day += 1
                else:
                    print(f"day: {day} -> {order}")
                    day += 1
            else:
                # even if empty
                print(f"day: {day} -> {order}")
                day += 1

    def get_plans_list(self):
        return self.nested_result_list

    def get_suppliers(self):
        return self.p1_supplier, self.p2_supplier

    def get_total_amount_to_restock(self):
        return self.amount_of_p1_to_restock, self.amount_of_p2_to_restock

    def get_total_cost_to_restock(self):
        return self.total_cost_of_p1, self.total_cost_of_p2
