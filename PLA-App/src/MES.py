# [TODO] Communicate to the Database
# [TODO] Lost Communication retrive "Last state" from the database
# [TODO] Execute Orders

import multiprocessing
import pickle
from modules import tcp_comm

from opcua import Client
from collections import Counter


url = "opc.tcp://localhost:4840"
client = Client(url)

P3 = 'P3'
done = 0


def process_tcp_comm():
    client_erp = tcp_comm.TCPClient()
    print("receiving...")
    client_erp.connect()
    while True:
        message = client_erp.receive(1024)
        if message is not None:
            data = pickle.loads(message)
            print(f"Received: {data}")

#exemplo de dados recebidos do erp
requests = [{'workpiece': 'P7', 'status': 'store2deliver'},
           {'workpiece': 'P7', 'status': 'store2deliver'},
           {'workpiece': 'P7', 'status': 'store2deliver'},
           {'workpiece': 'P6', 'status': 'makeANDdeliver'}]


# TODO toda vez que aparece um status de "makeANDdeliver" vc tem que checar no armazem antes de enviar
# se existem outras peças com o mesmo workpiece e o status store2deliver

#estado das maquinas:
M1livre = True  #T1, T2, T3
M2livre = True  #T1, T3, T4
M3livre = True  #T2, T3, T4
M4livre = True  #T1, T3, T4



           # 1      2     3     4
machines = [True, True, True, True]

machineUsed = 1

def makeP3(tipopeca, entrega):
    global M1livre, M3livre, machineUsed
    #alterar variaveis do plc para a peça andar ate ao segundo tapete

    if M1livre == True:
        #ativar maquina 1 no plc
        machineUsed == 1
        M1livre = False
    elif M3livre == True:
        #ativar maquina 3 no plc
        machineUsed == 3
        M1livre = False
    else:
        while True: #espera ate uma das maquinas ficar livre
            if (M1livre == True or M3livre==True) :
                if M1livre == True:
                    machineUsed == 1
                    break
                elif M3livre==True:
                    machineUsed == 3
                    break

    #alterar variaveis do plc de forma a iniciar a producao na maquina que ficou livre
    print(f'a peça esta a ser feita na maquina {machineUsed}')


def check_for_availability() -> bool:
    for available_machine in range(0,len(machines)):
        if machines[available_machine] == True:
            return available_machine+1

def total_equal_pieces():
    aux = []
    for order in requests:
        aux.append(order['workpiece'])

    count = Counter(aux) # {'P7':3, 'P6': 1}
    most_common = count.most_common(1) # {'P7': 3}
    return most_common[0][1] # 3


def machines_to_use():
    pass

def switch_case(x):
    if x == P3:
        print("You are going to make a P3")
        # P2->P3 (T2,10s)

    elif x == "p4":
        print("You are going to make a P4")
        # P2->P4 (T3,10s)

    elif x == "p5":
        print("You are going to make a P5")
        # P2->P4->P7->P9->P5 (T3,10s + T4,10s + T3,10s + T4,15s)

    elif x == "p6":
        print("You are going to make a P6")
        # P1->P6 (T1,20s)

    elif x == "p7":
        print("You are going to make a P7")
        # P2->P4->P7 (T3,10s + T4,10s)

    elif x == "p8":
        print("You are going to make a P8")
        # P1->P6->P8 (20s + 30s)

    elif x == "p9":
        print("You are going to make a P9")
        # P2->P4->P7->P9 (10s + 10s + 10s)
    else:
        print("error")


def showTerminal():
    pending = len(requests)
    produced = done
    print(f'Number of produced pieces: {produced}\nNumber of pending pieces: {pending}')

    """
       interface:
   Monitor the current production order list, as well as the status of each order received from the ERP. The status
   includes the number of pieces already produced, the number of pending pieces, the total production time of the order, etc. 
   The user interface should also provide enough information for the user to determine the status of that algorithm.
    """


'''
def process_tcp_comm():
    client_erp = tcp_comm.TCPClient()
    print("receiving...")
    client_erp.connect()
    while True:
        message = client_erp.receive(1024)
        print(f"Received: {message}")
'''


"""
def wh_m1(client):

    try:
        # Connect to server
        client.connect()

        var = client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.Geral.T1.cmd_R")
        print(var)
        if
            var.set_value(True)

    finally:
        client.disconnect()

    print("finish")
    return 0
"""

if __name__ == '__main__':
    tcp_process = multiprocessing.Process(target=process_tcp_comm)
    tcp_process.start()

    """while True:
        if pedidos != 0:
            switch_case(pedidos['pedido1']['workpiece'])
            del pedidos['pedido1']"""

    #switch_case(requests['pedido1']['workpiece'])

    total_equal_pieces()

          
    """
    try:
        # Connect to server
        client.connect()

        # Read node
        var = client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.Geral.T1.cmd_R")
        print(f'Value of node : {var.get_value()}')

        # Change value
        var.set_value(True)
        print(f'New value is : {var.get_value()}')
    """




