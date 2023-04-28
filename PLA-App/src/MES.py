# [TODO] Communicate to the Database
# [TODO] Lost Communication retrive "Last state" from the database
# [TODO] Execute Orders

#import multiprocessing
#from modules import tcp_comm

from opcua import Client

url = "opc.tcp://localhost:4840"
client = Client(url)

'''
def process_tcp_comm():
    client = tcp_comm.TCPClient()
    print("receiving...")
    client.connect()
    while True:
        message = client.receive(1024)
        print(f"Received: {message}")
'''


def wh_m1(client):

    try:
        # Connect to server
        client.connect()

        var = client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.Geral.WH_out.cmd_R")
        var.set_value(True)

        var2 = client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.Geral.WH_out.PieceToRemove")
        var2.set_value(2)

        var = client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.Geral.T1.cmd_R")
        var.set_value(True)

        var = client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.Geral.T1.cmd_L")
        var.set_value(False)

        var = client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.Geral.TR_Up_1.cmd_Rotation_plus")
        var.set_value(False)

        var = client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.Geral.TR_Up_1.cmd_Rotation_minus")
        var.set_value(True)

        var = client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.Geral.TR_Up_1.cmd_L")
        var.set_value(False)

        var = client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.Geral.TR_Up_1.cmd_R")
        var.set_value(True)

        while(True):
            var = client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.GVL.I[3]")
            if(var.get_value()==True):
                break

        var = client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.Geral.TR_Up_1.cmd_Rotation_plus")
        var.set_value(True)

        var = client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.Geral.TR_Up_1.cmd_Rotation_minus")
        var.set_value(False)

        var = client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.Geral.M1.cmd_R")
        var.set_value(True)

        var = client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.Geral.M1.cmd_L")
        var.set_value(False)

        while(True):
            var = client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.GVL.I[6]")
            if (var.get_value() == True):
                var = client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.Geral.M1.cmd_R")
                var.set_value(False)
                break
        #Desable
        var = client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.Geral.WH_out.cmd_R")
        var.set_value(False)

        var = client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.Geral.T1.cmd_R")
        var.set_value(False)

        var = client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.Geral.T1.cmd_L")
        var.set_value(False)

        var = client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.Geral.TR_Up_1.cmd_L")
        var.set_value(False)

        var = client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.Geral.TR_Up_1.cmd_R")
        var.set_value(False)

    finally:
        client.disconnect()

    print("finish")
    return 0


def wh_m3(client):
    try:
        # Connect to server
        client.connect()

        var = client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.Geral.WH_out.cmd_R")
        var.set_value(True)

        var2 = client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.Geral.WH_out.PieceToRemove")
        var2.set_value(2)

        var = client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.Geral.T1.cmd_R")
        var.set_value(True)

        var = client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.Geral.T1.cmd_L")
        var.set_value(False)

        var = client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.Geral.TR_Up_1.cmd_Rotation_plus")
        var.set_value(False)

        var = client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.Geral.TR_Up_1.cmd_Rotation_minus")
        var.set_value(True)

        var = client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.Geral.TR_Up_1.cmd_L")
        var.set_value(False)

        var = client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.Geral.TR_Up_1.cmd_R")
        var.set_value(True)

        var = client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.Geral.T2.cmd_R")
        var.set_value(True)

        var = client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.Geral.T2.cmd_L")
        var.set_value(False)

        var = client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.Geral.TR_Up_2.cmd_L")
        var.set_value(False)

        var = client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.Geral.TR_Up_2.cmd_R")
        var.set_value(True)

        var = client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.Geral.TTUp.cmd_ML")
        var.set_value(True)

        var = client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.Geral.TTUp.cmd_MR")
        var.set_value(False)

        while(True):
            var = client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.GVL.I[24]")
            if(var.get_value()==True):
                break

        var = client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.Geral.TR_Up_2.cmd_Rotation_plus")
        var.set_value(True)

        var = client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.Geral.TR_Up_2.cmd_Rotation_minus")
        var.set_value(False)

        var = client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.Geral.TTUp.cmd_L")
        var.set_value(False)

        var = client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.Geral.TTUp.cmd_R")
        var.set_value(True)

        var = client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.Geral.M3.cmd_R")
        var.set_value(True)

        var = client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.Geral.M3.cmd_L")
        var.set_value(False)

        while(True):
            var = client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.GVL.I[32]")
            if (var.get_value() == True):
                var = client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.Geral.M3.cmd_R")
                var.set_value(False)
                break
        #Desable
        var = client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.Geral.WH_out.cmd_R")
        var.set_value(False)

        var = client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.Geral.T1.cmd_R")
        var.set_value(False)

        var = client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.Geral.T1.cmd_L")
        var.set_value(False)

        var = client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.Geral.TR_Up_1.cmd_L")
        var.set_value(False)

        var = client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.Geral.TR_Up_1.cmd_R")
        var.set_value(False)

        var = client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.Geral.T2.cmd_R")
        var.set_value(False)

        var = client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.Geral.T2.cmd_L")
        var.set_value(False)

        var = client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.Geral.TR_Up_2.cmd_L")
        var.set_value(False)

        var = client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.Geral.TR_Up_2.cmd_R")
        var.set_value(False)

        var = client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.Geral.TTUp.cmd_L")
        var.set_value(False)

        var = client.get_node("ns=4;s=|var|CODESYS Control Win V3 x64.Application.Geral.TTUp.cmd_R")
        var.set_value(False)

    finally:
        client.disconnect()

    print("finish")
    return 0


if __name__ == '__main__':
    #tcp_process = multiprocessing.Process(target=process_tcp_comm)
    #tcp_process.start()

    wh_m1(client)

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



