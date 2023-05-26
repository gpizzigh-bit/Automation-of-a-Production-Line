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
        'P1': {'delivery_time': 1, 'price': 4, 'min_order_quantity': 4},
        'P2': {'delivery_time': 1, 'price': 4, 'min_order_quantity': 4}
    }
}

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
