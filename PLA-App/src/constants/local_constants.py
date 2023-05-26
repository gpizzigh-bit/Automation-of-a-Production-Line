suppliers = {
    'A': {
        'P1': {'delivery_time': 3, 'price': 10, 'min_order_quantity': 20},
        'P2': {'delivery_time': 5, 'price': 12, 'min_order_quantity': 30}
    },
    'B': {
        'P1': {'delivery_time': 4, 'price': 9, 'min_order_quantity': 25},
        'P2': {'delivery_time': 6, 'price': 11, 'min_order_quantity': 35}
    },
    'C': {
        'P1': {'delivery_time': 1, 'price': 8, 'min_order_quantity': 15},
        'P2': {'delivery_time': 2, 'price': 10, 'min_order_quantity': 20}
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
