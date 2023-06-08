suppliers = {
    'A': {
        'P1': {'delivery_time': 4, 'price': 30, 'min_order_quantity': 16},
        'P2': {'delivery_time': 4, 'price': 10, 'min_order_quantity': 16}
    },
    'B': {
        'P1': {'delivery_time': 2, 'price': 45, 'min_order_quantity': 8},
        'P2': {'delivery_time': 2, 'price': 15, 'min_order_quantity': 8}
    },
    'C': {
        'P1': {'delivery_time': 1, 'price': 55, 'min_order_quantity': 4},
        'P2': {'delivery_time': 1, 'price': 18, 'min_order_quantity': 4}
    }
}

STORE_GLOBAL = "makeANDstore"
DELIVER_GLOBAL = "makeANDdeliver"
STORE2DELIVER = "store2deliver"
STORE2DELIVER_WAREHOUSE_LIMIT = 17  # 17
P1_RESTOCK_STR = "P1 restock"
P2_RESTOCK_STR = "P2 restock"
P1_AND_P2_RESTOCK_STR = "P1 and P2 restock"
LIMIT_OF_DELIVER_BY_DAY = 5
RESTOCK_THRESHOLD = {"P1": 10, "P2": 10}
RAW_PIECES_THRESHOLD = 30
P1_RESTOCK_LIMIT_BY_DAY = 9  # pieces
P2_RESTOCK_LIMIT_BY_DAY = 11  # pieces

erp_to_mes_test_data = [['P1 and P2 restock'],

                        [{'workpiece': 'P4', 'status': 'makeANDstore'},
                         {'workpiece': 'P4', 'status': 'makeANDstore'},
                         {'workpiece': 'P4', 'status': 'makeANDstore'},
                         {'workpiece': 'P4', 'status': 'makeANDstore'}],

                        [{'workpiece': 'P6', 'status': 'makeANDdeliver'},
                         {'workpiece': 'P7', 'status': 'store2deliver'},
                         {'workpiece': 'P7', 'status': 'store2deliver'},
                         {'workpiece': 'P7', 'status': 'store2deliver'}],

                        [{'workpiece': 'P7', 'status': 'store2deliver'},
                         {'workpiece': 'P4', 'status': 'makeANDstore'},
                         {'workpiece': 'P4', 'status': 'makeANDstore'},
                         {'workpiece': 'P4', 'status': 'makeANDstore'}],

                        [{'workpiece': 'P4', 'status': 'makeANDstore'},
                         {'workpiece': 'P7', 'status': 'makeANDdeliver'},
                         {'workpiece': 'P7', 'status': 'makeANDdeliver'},
                         {'workpiece': 'P7', 'status': 'makeANDdeliver'}],

                        ['delivery day']]
