# [TODO] Communicate to the Database
# [TODO] Lost Communication retrive "Last state" from the database
# [TODO] Execute Orders

import multiprocessing
import pickle
from modules import tcp_comm

from opcua import Client, ua
import pyfiglet
from termcolor import colored
import time


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
#store2make sao peças usadas para fazer outras. nao devem ser enviadas com o make and deliver, mm  q sejam do mm tipo

def switch_case(x, machine_number, todo, c, a):
    c=c
    p = int(x[1:])
    if x == 'restock day':
        #fazer o restock
        print('restock')

    elif x == 'P3':
        print("You are going to make a P3 from a P2, using a T2")
        towrite = 1  # peça a pegar do armazem - ERRADA !!!!!!!!!
        if machine_number == 1:
            string1 = "ns=4;s=|var|CODESYS Control Win V3 x64.Application.WH_M1_1.Piece"
            string2 = "ns=4;s=|var|CODESYS Control Win V3 x64.Application.WH_M1_1.WH_M1"
            #decidir onde mostar terminal, usando o tempo inicial a p calcular tempo que passou
            send_from_wh_to_machine(string1, string2, towrite)
            #fazer a peça e enviar para o armazem
            status_decision(c, p, todo)

        elif machine_number == 3:
            string1="ns=4;s=|var|CODESYS Control Win V3 x64.Application.WH_M3.Piece"
            string2="ns=4;s=|var|CODESYS Control Win V3 x64.Application.WH_M3.WH_M3"
            send_from_wh_to_machine(string1, string2, towrite)

    elif x == 'P4':
        print("You are going to make a P4 from a P2, using a T3")
        towrite = 2  # peça a pegar do armazem
        if machine_number==1:
            string1 = "ns=4;s=|var|CODESYS Control Win V3 x64.Application.WH_M1_1.Piece"
            string2 = "ns=4;s=|var|CODESYS Control Win V3 x64.Application.WH_M1_1.WH_M1"
            send_from_wh_to_machine(string1, string2, towrite)

        elif machine_number==2: #acrescentar condição para esperar que a maquina 1 esteja livre
            string1 = "ns=4;s=|var|CODESYS Control Win V3 x64.Application.WH_M1_1.Piece"
            string2 = "ns=4;s=|var|CODESYS Control Win V3 x64.Application.WH_M1_1.WH_M1"
            send_from_wh_to_machine(string1, string2, towrite)
            string3 = "ns=4;s=|var|CODESYS Control Win V3 x64.Application.M1_M2.M1_M2"
            send_from_machine1_to_machine2(string3)


        elif machine_number==3:
            string1 = "ns=4;s=|var|CODESYS Control Win V3 x64.Application.WH_M3.Piece"
            string2 = "ns=4;s=|var|CODESYS Control Win V3 x64.Application.WH_M3.WH_M3"
            send_from_wh_to_machine(string1, string2, towrite)

        elif machine_number==4:
            string1 = "ns=4;s=|var|CODESYS Control Win V3 x64.Application.WH_M4.Piece"
            string2 = "ns=4;s=|var|CODESYS Control Win V3 x64.Application.WH_M4.WH_M4"
            send_from_wh_to_machine(string1, string2, towrite)


    elif x == 'P5':
        print("You are going to make a P5 from a P9, using a T4")
        towrite = 9  # peça a pegar do armazem
        #if machine_number == 2:
        #elif machine_number == 3:
        #elif machine_number == 4:


    elif x == 'P6':
        print("You are going to make a P6 from a P3, using a T1")
        towrite = 3  # peça a pegar do armazem
        #if machine_number == 1:
        #elif machine_number == 2:
        #elif machine_number == 4:


    elif x == 'P7':
        print("You are going to make a P7 from a P4, using a T4")
        towrite = 4  # peça a pegar do armazem
        #if machine_number == 2:
        #elif machine_number == 3:
        #elif machine_number == 4:


    elif x == 'P8':
        print("You are going to make a P8 from a P6, using a T3")
        towrite = 6  # peça a pegar do armazem
        #if machine_number == 1:
        #elif machine_number == 2:
        #elif machine_number == 3:
        #elif machine_number == 4:


    elif x == 'P9':
        print("You are going to make a P9 from a P7, using a T3")
        towrite = 7  # peça a pegar do armazem
        #if machine_number == 1:
        #elif machine_number == 2:
        #elif machine_number == 3:
        #elif machine_number == 4:

    else:
        print("error")

def send_from_wh_to_machine(string1, string2, towrite):
    var = client.get_node(string1)
    print(f'por alterar: {var.get_value()}')
    data_value = ua.DataValue(ua.Variant(towrite, varianttype=ua.VariantType.Int16))
    var.set_value(data_value)
    print(f'ja alterada:{var.get_value()}')

    var = client.get_node(string2)
    print(f'por alterar: {var.get_value()}')
    var.set_value(True)
    print(f'ja alterada:{var.get_value()}')

def send_from_machine1_to_machine2(string3):
    var = client.get_node(string3)
    print(f'por alterar: {var.get_value()}')
    var.set_value(True)
    print(f'ja alterada:{var.get_value()}')

def status_decision(c,p, todo): #por acabar !!!!
    if todo == 'store2deliver':
        if p == 3:
            c[0] = c[0] + 1
        elif p == 4:
            c[1] = c[1] + 1
        elif p == 5:
            c[2] = c[2] + 1
        elif p == 6:
            c[3] = c[3] + 1
        elif p == 7:
            c[4] = c[4] + 1
        elif p == 8:
            c[5] = c[5] + 1
        elif p == 9:
            c[6] = c[6] + 1
    elif todo == 'makeANDdeliver':
        n=c[p-3]
        #enviar as peças. parametros: p (inteiro) ; numero de peças: n
        show_terminal_shipping(requests, time, p, n)
        c[p-3]=0

def show_terminal(requests, id, time, init):
    print('-----------------------------------------------------------------------')
    title=pyfiglet.figlet_format('MES TERMINAL')
    title=colored(title, "blue")
    print(title)
    print('-----------------------------------------------------------------------')
    produced=id
    pending = 4-produced
    workpiece_number=[0,0,0,0]
    string1='               First Order:'
    stringf1=colored(string1, attrs=['bold'])
    string2='               Second Order:'
    stringf2 = colored(string2, attrs=['bold'])
    string3='               Third Order:'
    stringf3 = colored(string3, attrs=['bold'])
    string4='               Fourth Order:'
    stringf4 = colored(string4, attrs=['bold'])
    string5='         Status:'
    string6='        Status:'
    stringf5 = colored(string5, attrs=['bold'])
    stringf6 = colored(string6, attrs=['bold'])
    if len(requests)==1:
        string ='                             RESTOCK DAY'
        stringg='          pieces P1 and P2 are being stored in the warehouse'
        stringf = colored(string, 'red', attrs=['bold'])
        print(stringf)
        print(stringg)
    elif len(requests)==4:
        string = '                  Number of produced pieces today:'
        stringf = colored(string, 'yellow', attrs=['bold'])
        print(f'{stringf} {produced}')
        string = '                     Number of pending pieces:'
        stringf = colored(string, 'yellow', attrs=['bold'])
        print(f'{stringf} {pending}\n')
        string = '                              Orders:'
        stringf = colored(string, 'red', attrs=['bold'])
        print(stringf)
        for i in range(4):
            piece = requests[i]['workpiece']
            number = int(piece[1:])
            workpiece_number[i] = number
        if id==0:
            if init==1:
                print(f'{stringf1} P{workpiece_number[0]}{stringf5} About to start')
            elif init==0:
                print(f'{stringf1} P{workpiece_number[0]}{stringf5} Making the piece')
            print(f'{stringf2} P{workpiece_number[1]}{stringf6} Waiting')
            print(f'{stringf3} P{workpiece_number[2]}{stringf5} Waiting')
            print(f'{stringf4} P{workpiece_number[3]}{stringf6} Waiting\n')
        elif id==1:
            print(f'{stringf1} P{workpiece_number[0]}{stringf5} Done')
            print(f'{stringf2} P{workpiece_number[1]}{stringf6} Making the piece')
            print(f'{stringf3} P{workpiece_number[2]}{stringf5} Waiting')
            print(f'{stringf4} P{workpiece_number[3]}{stringf6} Waiting\n')
        elif id==2:
            print(f'{stringf1} P{workpiece_number[0]}{stringf5} Done')
            print(f'{stringf2} P{workpiece_number[1]}{stringf6} Done')
            print(f'{stringf3} P{workpiece_number[2]}{stringf5} Making the piece')
            print(f'{stringf4} P{workpiece_number[3]} Waiting\n')
        elif id==3:
            print(f'{stringf1} P{workpiece_number[0]}{stringf5} Done')
            print(f'{stringf2} P{workpiece_number[1]}{stringf6} Done')
            print(f'{stringf3} P{workpiece_number[2]}{stringf5} Done')
            print(f'{stringf4} P{workpiece_number[3]}{stringf6} Making the piece\n')
        string = '           Time passed since production started:'
        stringf = colored(string, 'green', attrs=['bold'])
        print(f'{stringf} {time} segundos')

    print('-----------------------------------------------------------------------')

def show_terminal_end(requests, time):
    print('-----------------------------------------------------------------------')
    title = pyfiglet.figlet_format('MES TERMINAL')
    title = colored(title, "blue")
    print(title)
    print('-----------------------------------------------------------------------')
    produced = 4
    pending = 0
    workpiece_number = [0, 0, 0, 0]
    string1 = '               First Order:'
    stringf1 = colored(string1, attrs=['bold'])
    string2 = '               Second Order:'
    stringf2 = colored(string2, attrs=['bold'])
    string3 = '               Third Order:'
    stringf3 = colored(string3, attrs=['bold'])
    string4 = '               Fourth Order:'
    stringf4 = colored(string4, attrs=['bold'])
    string5 = '         Status:'
    string6 = '        Status:'
    stringf5 = colored(string5, attrs=['bold'])
    stringf6 = colored(string6, attrs=['bold'])
    if len(requests) == 1:
        string = '                           RESTOCK FINISHED'
        stringg = '            pieces P1 and P2 are now stored in the warehouse'
        stringf = colored(string, 'red', attrs=['bold'])
        print(stringf)
        print(stringg)
    elif len(requests) == 4:
        string = '                  Number of produced pieces today:'
        stringf = colored(string, 'yellow', attrs=['bold'])
        print(f'{stringf} {produced}')
        string = '                     Number of pending pieces:'
        stringf = colored(string, 'yellow', attrs=['bold'])
        print(f'{stringf} {pending}\n')
        string = '                              Orders:'
        stringf = colored(string, 'red', attrs=['bold'])
        print(stringf)
        for i in range(4):
            piece = requests[i]['workpiece']
            number = int(piece[1:])
            workpiece_number[i] = number

            print(f'{stringf1} P{workpiece_number[0]}{stringf5} Done')
            print(f'{stringf2} P{workpiece_number[1]}{stringf6} Done')
            print(f'{stringf3} P{workpiece_number[2]}{stringf5} Done')
            print(f'{stringf4} P{workpiece_number[3]}{stringf6} Done\n')
        string = '           Time passed since production started:'
        stringf = colored(string, 'green', attrs=['bold'])
        print(f'{stringf} {time} segundos')

    print('-----------------------------------------------------------------------')

"""
interface:
The status includes the number of pieces already produced, the number of pending pieces, the total production time of the order, etc. 
The user interface should also provide enough information for the user to determine the status of that algorithm.
"""

def show_terminal_shipping(requests, time, p, n):
    print('-----------------------------------------------------------------------')
    title = pyfiglet.figlet_format('MES TERMINAL')
    title = colored(title, "blue")
    print(title)
    print('-----------------------------------------------------------------------')
    produced = 4
    pending = 0

    string = '                  Number of produced pieces today:'
    stringf = colored(string, 'yellow', attrs=['bold'])
    print(f'{stringf} {produced}')
    string = '                     Number of pending pieces:'
    stringf = colored(string, 'yellow', attrs=['bold'])
    print(f'{stringf} {pending}\n')
    n=str(n)
    p=str(p)
    string = '                   Delivering '+n
    string = string+ " pieces of type P"+p
    stringf = colored(string, 'red', attrs=['bold'])
    print(f'{stringf}\n')

    string = '           Time passed since production started:'
    stringf = colored(string, 'green', attrs=['bold'])
    print(f'{stringf} {time} segundos')

    print('-----------------------------------------------------------------------')


def get_requests():
    global requests
    tools_finais = [0, 0, 0, 0]
    for i in range(4):
        piece = requests[i]['workpiece']
        number = int(piece[1:])
        tools_finais[i] = number
    return tools_finais
def get_tools_finais(tools_finais):
    pecas_tools = [2, 3, 4, 1, 4, 3, 3]
    # P3,P4,P5,P6,P7,P8,P9
    for i in range(4):
        tools_finais[i]=pecas_tools[tools_finais[i]-3]

    return tools_finais
def check_if_possible(i, j, tools_finais):
    k=0
    machines= [
        [1,2,3],
        [1,3,4],
        [2,3,4],
        [1,3,4]]

    for k in range(3):
        if machines[i][k]==tools_finais[j]:
            return 1

    return 0
def alocacao_pecas(tools_iniciais, tools_finais):

    i=0
    j=0

    resultado = [
        [0,0,0,0],
        [0,0,0,0]]
    #[tool_M1, tool_M2, tool_M3, tool_M4] , id da peça a ser feita na [M1, M2, M3, M4]

    while i<4:
       if tools_iniciais[i] == tools_finais[i]:
            resultado[0][i] = tools_finais[i]
            resultado[1][i] = i+1
            tools_finais[i] = 0
            tools_iniciais[i] = 0
            i=i+1
       else:
           i=i+1


    i=0

    while i<4:
        while j<4:
            if tools_iniciais[i] == tools_finais[j] and tools_finais[j]!=0:
                resultado[0][i]= tools_finais[j]
                resultado[1][i]=j+1
                tools_finais[j]=0
                tools_iniciais[i]=0
                j=4
            else:
                j=j+1
        i=i+1
        j=0

    print(tools_finais)
    print(tools_iniciais)
    print(resultado)
    i=0
    j=0
    count=0

    for i in range(4):
        if tools_finais[i]!=0:
            count=count+1

    i=0
    print(count)

    if count==1:
        print("Only one machine needs to change the tool")
        count1(tools_iniciais, tools_finais, resultado)

    elif count==2:
        print("Two machines have to change the tool")
        count2(tools_iniciais, tools_finais, resultado)

    elif count==3:
        print("Three machines have to change the tool")

    i=0
    for i in range(4):
        print(f"Machine {i + 1}: tool {resultado[0][i]} , is going to make a piece with the id={resultado[1][i]}")

    return resultado
def count1(tools_iniciais, tools_finais, resultado):
    j=0
    i=0
    for i in range(4):
        if tools_finais[i]!=0:
            j=i
            i=4
    i=0

    while i<4:
        if resultado[0][i] == 0:
            resultado[0][i] = tools_finais[j]
            resultado[1][i] = j+1
            print(
                f'The machine {i + 1} needs to change the tool from a T{tools_iniciais[i]} to a T{tools_finais[i]}')
            i=4
        else:
            i=i+1
def count2(tools_iniciais, tools_finais, resultado):
    j = [[0,0],[0,0]]
    i = 0
    k = 0
    count=2
    tools_finais[2]=2

    for i in range(4):
        if tools_finais[i] != 0:
            j[0][k] = tools_finais[i]
            j[1][k] = i
            k=k+1

    i=0

    print('teste')
    print(j)
    print(f'tools iniciais: {tools_iniciais}')
    print(f'tools finais:{tools_finais}')
    print(f'result{resultado}')

    for i in range(2):
        if j[0][i]==2:
            if resultado[0][0]==0:  #M1
                resultado [0][0]=tools_finais[j[1][i]]
                resultado [1][0]=tools_finais[j[1][i]] + 1
                print(f'tools_finais: {tools_finais}')
                print(
                    f'The machine 1 needs to change the tool from a T{tools_iniciais[0]} to a T2')
                tools_finais[j[1][i]]=0
                tools_iniciais[0]=0
                j[0][0]=0
                j[1][0]=0
                count=count-1

            elif resultado[0][2]==0: #M3
                resultado[0][2] = tools_finais[j[1][i]]
                resultado[1][2] = tools_finais[j[1][i]] + 1
                print(
                    f'The machine 3 needs to change the tool from a T{tools_iniciais[2]} to a T2')
                tools_finais[j[1][i]] = 0
                tools_iniciais[2]=0
                j[0][1] = 0
                j[1][1] = 0
                count=count-1
            else:
                print('BIG ERROR')

    i=0
    k=0
    print (j)
    """while count>0:
        for i in range(4):
            if tools_finais[i] != 0:
                j[0][k] = tools_finais[i]
                j[1][k] = i
                k = k + 1
        print(j)"""

if __name__ == '__main__':
    """tcp_process = multiprocessing.Process(target=process_tcp_comm)
    tcp_process.start()

    

    # Connect to server
    url = "opc.tcp://localhost:4840"
    client = Client(url)
    client.connect()
    c=[0,0,0,0,0,0,0]

    while True:
        #receive and store requests from the erp
        size=len(requests)
        id=0
        show_terminal(requests, id, 0, 1)
        a = time.time()

        for id in range(size):
            show_terminal(requests, id, 0, 0)
            string=requests[id]['workpiece']
            todo=requests[id]['status']
            #definir maquina a utilizar, excepto se for restock
            switch_case(string, maquina_a_usar, todo, c, a)
            b = time.time()
            b=b-a
            show_terminal_end(requests, b)"""

    #dados para testar:
    todo='store2deliver'
    string = 'P3'
    maquina_a_usar=1
    id = 0
    a=0
    time = 2
    show_terminal(requests, id, time, 1)

    #switch_case(string, maquina_a_usar, todo, a)

    #client.disconnect()




