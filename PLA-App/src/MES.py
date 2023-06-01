import threading
import time

import pyfiglet
from opcua import ua, Client
from termcolor import colored
from modules.database_orders_class import Database, Stock, Orders, Concluded, Statistics
from modules import tcp_comm
import numpy as np
from constants.local_constants import *

TCP_IP = "127.0.0.1"  # local
TCP_PORT = 12345

FEEDBACK_MSG = "Message Received!"
HANDSHAKE_FROM_MES = "HANDSHAKE FROM MES"

P1_RESTOCK_TIME = 7
P2_RESTOCK_TIME = 6

machines_state = [1, 1, 2, 1]

orders_obj = Orders()
conclude_obj = Concluded()
stats = Statistics()


class ThreadedServer(threading.Thread):
    def __init__(self):
        # create the server object for communication
        super().__init__()
        self.server = tcp_comm.TCPServer()
        self.signal_to_stop = False
        self.msg = None

    def run(self) -> None:
        while self.signal_to_stop is not True:
            self.msg = self.server.receive(1024)
            self.server.send(FEEDBACK_MSG)

    def get_message(self):
        return self.msg

    def stop(self):
        self.signal_to_stop = True


def tool_changer(machine, new_tool, old_tool):
    machine_tools = [
        [1, 2, 3],
        [1, 3, 4],
        [2, 3, 4],
        [1, 3, 4],
    ]
    for i in range(3):
        if old_tool == machine_tools[machine - 1][i]:
            break
    # i=posiçao da old_tool na machine_tools
    for j in range(3):
        if new_tool == machine_tools[machine - 1][j]:
            break
    # j=posiçao da new_tool na machine tools

    decision = "empty"
    string = "ns=4;s=|var|CODESYS Control Win V3 x64.Application.Geral.M1.cmd_R_minus"

    if i == 0:
        if j == 2:
            decision = "minus"
        elif j == 1:
            decision = "plus"
    elif i == 1:
        if j == 0:
            decision = "minus"
        elif j == 2:
            decision = "plus"
    elif i == 2:
        if j == 1:
            decision = "minus"
        elif j == 0:
            decision = "plus"

    if machine == 1 and decision == "minus":
        string = "ns=4;s=|var|CODESYS Control Win V3 x64.Application.Geral.M1.cmd_R_minus"
    elif machine == 1 and decision == "plus":
        string = "ns=4;s=|var|CODESYS Control Win V3 x64.Application.Geral.M1.cmd_R_plus"
    elif machine == 2 and decision == "minus":
        string = "ns=4;s=|var|CODESYS Control Win V3 x64.Application.Geral.M2.cmd_R_minus"
    elif machine == 2 and decision == "plus":
        string = "ns=4;s=|var|CODESYS Control Win V3 x64.Application.Geral.M2.cmd_R_plus"
    elif machine == 3 and decision == "minus":
        string = "ns=4;s=|var|CODESYS Control Win V3 x64.Application.Geral.M3.cmd_R_minus"
    elif machine == 3 and decision == "plus":
        string = "ns=4;s=|var|CODESYS Control Win V3 x64.Application.Geral.M3.cmd_R_plus"
    elif machine == 4 and decision == "minus":
        string = "ns=4;s=|var|CODESYS Control Win V3 x64.Application.Geral.M4.cmd_R_minus"
    elif machine == 4 and decision == "plus":
        string = "ns=4;s=|var|CODESYS Control Win V3 x64.Application.Geral.M4.cmd_R_plus"

    setting_a_variable_true(string)
    machines_state[machine - 1] = new_tool
    print(f'changing from T{old_tool} to a T{new_tool} on machine {machine}')


def machine_decision(type, next_type, machines_state, first_iteration, id, next_machine_to_use, client):
    import time
    pecas_tools = [2, 3, 4, 1, 4, 3, 3]
    # tool needed :P3,P4,P5,P6,P7,P8,P9
    options = [
        [1, 3],  # P3: M1, M3
        [2, 1, 3, 4],  # P4: M2, M1, M3, M4
        [2, 3, 4],  # P5: M2, M3, M4
        [2, 1, 4],  # P6: M2, M1, M4
        [2, 3, 4],  # P7: M2, M3, M4
        [2, 1, 3, 4],  # P8: M2, M1, M3, M4
        [2, 1, 3, 4, ]  # P9: M2, M1, M3, M4
    ]

    if id != 3:
        type = int(type[1:])
        next_type = int(next_type[1:])
        tool_needed = pecas_tools[type - 3]
        next_tool_needed = pecas_tools[next_type - 3]
        machines_possible = options[type - 3]
        next_machines_possible = options[next_type - 3]
        i = 0

        if type == 3:
            if first_iteration == 1:
                machine_to_use = 0
                next_machine_to_use = 0
                for i in range(len(machines_possible)):
                    if tool_needed == machines_state[machines_possible[i] - 1]:
                        machine_to_use = machines_possible[i]
                        break
                if machine_to_use == 0:
                    tool_changer(machines_possible[0], tool_needed, machines_state[machines_possible[0] - 1])
                    time.sleep(20)
                    machine_to_use = machines_possible[0]
            else:
                machine_to_use = next_machine_to_use
                next_machine_to_use = 0

            for i in range(len(next_machines_possible)):
                if next_tool_needed == machines_state[next_machines_possible[i] - 1] and next_machines_possible[
                    i] != machine_to_use:
                    if ((next_machines_possible[i] == 2 and machine_to_use == 1) or (
                            next_machines_possible[i] == 1 and machine_to_use == 2) or (
                            next_machines_possible[i] == 3 and machine_to_use == 4) or (
                            next_machines_possible[i] == 4 and machine_to_use == 3)):
                        next_machine_to_use = 0
                    else:
                        next_machine_to_use = next_machines_possible[i]
                        break

            if next_machine_to_use == 0:
                if machine_to_use == 2:
                    for i in range(len(next_machines_possible)):
                        if next_machines_possible[i] == 3:
                            tool_changer(next_machines_possible[i], next_tool_needed,
                                         machines_state[next_machines_possible[i] - 1])
                            next_machine_to_use = next_machines_possible[i]
                            break
                        elif next_machines_possible[i] == 4:
                            tool_changer(next_machines_possible[i], next_tool_needed,
                                         machines_state[next_machines_possible[i] - 1])
                            next_machine_to_use = next_machines_possible[i]
                            break
                elif machine_to_use == 1:
                    for i in range(len(next_machines_possible)):
                        if next_machines_possible[i] == 3:
                            tool_changer(next_machines_possible[i], next_tool_needed,
                                         machines_state[next_machines_possible[i] - 1])
                            next_machine_to_use = next_machines_possible[i]
                            break
                        elif next_machines_possible[i] == 4:
                            tool_changer(next_machines_possible[i], next_tool_needed,
                                         machines_state[next_machines_possible[i] - 1])
                            next_machine_to_use = next_machines_possible[i]
                            break
                elif machine_to_use == 3:
                    for i in range(len(next_machines_possible)):
                        if next_machines_possible[i] == 2:
                            tool_changer(next_machines_possible[i], next_tool_needed,
                                         machines_state[next_machines_possible[i] - 1])
                            next_machine_to_use = next_machines_possible[i]
                            break
                        elif next_machines_possible[i] == 1:
                            tool_changer(next_machines_possible[i], next_tool_needed,
                                         machines_state[next_machines_possible[i] - 1])
                            next_machine_to_use = next_machines_possible[i]
                            break
                elif machine_to_use == 4:
                    for i in range(len(next_machines_possible)):
                        if next_machines_possible[i] == 2:
                            tool_changer(next_machines_possible[i], next_tool_needed,
                                         machines_state[next_machines_possible[i] - 1])
                            next_machine_to_use = next_machines_possible[i]
                            break
                        elif next_machines_possible[i] == 1:
                            tool_changer(next_machines_possible[i], next_tool_needed,
                                         machines_state[next_machines_possible[i] - 1])
                            next_machine_to_use = next_machines_possible[i]
                            break
        elif type == 4:
            if first_iteration == 1:
                next_machine_to_use = 0
                machine_to_use = 0
                for i in range(len(machines_possible)):
                    if tool_needed == machines_state[machines_possible[i] - 1]:
                        machine_to_use = machines_possible[i]
                        break
                if machine_to_use == 0:
                    tool_changer(machines_possible[0], tool_needed, machines_state[machines_possible[0] - 1])
                    time.sleep(20)
                    machine_to_use = machines_possible[0]
            else:
                machine_to_use = next_machine_to_use
                next_machine_to_use = 0

            for i in range(len(next_machines_possible)):
                if next_tool_needed == machines_state[next_machines_possible[i] - 1] and next_machines_possible[
                    i] != machine_to_use:
                    if ((next_machines_possible[i] == 2 and machine_to_use == 1) or (
                            next_machines_possible[i] == 1 and machine_to_use == 2) or (
                            next_machines_possible[i] == 3 and machine_to_use == 4) or (
                            next_machines_possible[i] == 4 and machine_to_use == 3)):
                        next_machine_to_use = 0
                    else:
                        next_machine_to_use = next_machines_possible[i]
                        break

            if next_machine_to_use == 0:
                if machine_to_use == 2:
                    for i in range(len(next_machines_possible)):
                        if next_machines_possible[i] == 3:
                            tool_changer(next_machines_possible[i], next_tool_needed,
                                         machines_state[next_machines_possible[i] - 1])
                            next_machine_to_use = next_machines_possible[i]
                            break
                        elif next_machines_possible[i] == 4:
                            tool_changer(next_machines_possible[i], next_tool_needed,
                                         machines_state[next_machines_possible[i] - 1])
                            next_machine_to_use = next_machines_possible[i]
                            break
                elif machine_to_use == 1:
                    for i in range(len(next_machines_possible)):
                        if next_machines_possible[i] == 3:
                            tool_changer(next_machines_possible[i], next_tool_needed,
                                         machines_state[next_machines_possible[i] - 1])
                            next_machine_to_use = next_machines_possible[i]
                            break
                        elif next_machines_possible[i] == 4:
                            tool_changer(next_machines_possible[i], next_tool_needed,
                                         machines_state[next_machines_possible[i] - 1])
                            next_machine_to_use = next_machines_possible[i]
                            break
                elif machine_to_use == 3:
                    for i in range(len(next_machines_possible)):
                        if next_machines_possible[i] == 2:
                            tool_changer(next_machines_possible[i], next_tool_needed,
                                         machines_state[next_machines_possible[i] - 1])
                            next_machine_to_use = next_machines_possible[i]
                            break
                        elif next_machines_possible[i] == 1:
                            tool_changer(next_machines_possible[i], next_tool_needed,
                                         machines_state[next_machines_possible[i] - 1])
                            next_machine_to_use = next_machines_possible[i]
                            break
                elif machine_to_use == 4:
                    for i in range(len(next_machines_possible)):
                        if next_machines_possible[i] == 2:
                            tool_changer(next_machines_possible[i], next_tool_needed,
                                         machines_state[next_machines_possible[i] - 1])
                            next_machine_to_use = next_machines_possible[i]
                            break
                        elif next_machines_possible[i] == 1:
                            tool_changer(next_machines_possible[i], next_tool_needed,
                                         machines_state[next_machines_possible[i] - 1])
                            next_machine_to_use = next_machines_possible[i]
                            break
        elif type == 5:
            if first_iteration == 1:
                next_machine_to_use = 0
                machine_to_use = 0
                for i in range(len(machines_possible)):
                    if tool_needed == machines_state[machines_possible[i] - 1]:
                        machine_to_use = machines_possible[i]
                        break
                if machine_to_use == 0:
                    tool_changer(machines_possible[0], tool_needed, machines_state[machines_possible[0] - 1])
                    time.sleep(20)
                    machine_to_use = machines_possible[0]
            else:
                machine_to_use = next_machine_to_use
                next_machine_to_use = 0

            for i in range(len(next_machines_possible)):
                if next_tool_needed == machines_state[next_machines_possible[i] - 1] and next_machines_possible[
                    i] != machine_to_use:
                    if ((next_machines_possible[i] == 2 and machine_to_use == 1) or (
                            next_machines_possible[i] == 1 and machine_to_use == 2) or (
                            next_machines_possible[i] == 3 and machine_to_use == 4) or (
                            next_machines_possible[i] == 4 and machine_to_use == 3)):
                        next_machine_to_use = 0
                    else:
                        next_machine_to_use = next_machines_possible[i]
                        break

            if next_machine_to_use == 0:
                if machine_to_use == 2:
                    for i in range(len(next_machines_possible)):
                        if next_machines_possible[i] == 3:
                            tool_changer(next_machines_possible[i], next_tool_needed,
                                         machines_state[next_machines_possible[i] - 1])
                            next_machine_to_use = next_machines_possible[i]
                            break
                        elif next_machines_possible[i] == 4:
                            tool_changer(next_machines_possible[i], next_tool_needed,
                                         machines_state[next_machines_possible[i] - 1])
                            next_machine_to_use = next_machines_possible[i]
                            break
                elif machine_to_use == 1:
                    for i in range(len(next_machines_possible)):
                        if next_machines_possible[i] == 3:
                            tool_changer(next_machines_possible[i], next_tool_needed,
                                         machines_state[next_machines_possible[i] - 1])
                            next_machine_to_use = next_machines_possible[i]
                            break
                        elif next_machines_possible[i] == 4:
                            tool_changer(next_machines_possible[i], next_tool_needed,
                                         machines_state[next_machines_possible[i] - 1])
                            next_machine_to_use = next_machines_possible[i]
                            break
                elif machine_to_use == 3:
                    for i in range(len(next_machines_possible)):
                        if next_machines_possible[i] == 2:
                            tool_changer(next_machines_possible[i], next_tool_needed,
                                         machines_state[next_machines_possible[i] - 1])
                            next_machine_to_use = next_machines_possible[i]
                            break
                        elif next_machines_possible[i] == 1:
                            tool_changer(next_machines_possible[i], next_tool_needed,
                                         machines_state[next_machines_possible[i] - 1])
                            next_machine_to_use = next_machines_possible[i]
                            break
                elif machine_to_use == 4:
                    for i in range(len(next_machines_possible)):
                        if next_machines_possible[i] == 2:
                            tool_changer(next_machines_possible[i], next_tool_needed,
                                         machines_state[next_machines_possible[i] - 1])
                            next_machine_to_use = next_machines_possible[i]
                            break
                        elif next_machines_possible[i] == 1:
                            tool_changer(next_machines_possible[i], next_tool_needed,
                                         machines_state[next_machines_possible[i] - 1])
                            next_machine_to_use = next_machines_possible[i]
                            break
        elif type == 6:
            if first_iteration == 1:
                next_machine_to_use = 0
                machine_to_use = 0
                for i in range(len(machines_possible)):
                    if tool_needed == machines_state[machines_possible[i] - 1]:
                        machine_to_use = machines_possible[i]
                        break
                if machine_to_use == 0:
                    tool_changer(machines_possible[0], tool_needed, machines_state[machines_possible[0] - 1])
                    time.sleep(20)
                    machine_to_use = machines_possible[0]
            else:
                machine_to_use = next_machine_to_use
                next_machine_to_use = 0

            for i in range(len(next_machines_possible)):
                if next_tool_needed == machines_state[next_machines_possible[i] - 1] and next_machines_possible[
                    i] != machine_to_use:
                    if ((next_machines_possible[i] == 2 and machine_to_use == 1) or (
                            next_machines_possible[i] == 1 and machine_to_use == 2) or (
                            next_machines_possible[i] == 3 and machine_to_use == 4) or (
                            next_machines_possible[i] == 4 and machine_to_use == 3)):
                        next_machine_to_use = 0
                    else:
                        next_machine_to_use = next_machines_possible[i]
                        break

            if next_machine_to_use == 0:
                if machine_to_use == 2:
                    for i in range(len(next_machines_possible)):
                        if next_machines_possible[i] == 3:
                            tool_changer(next_machines_possible[i], next_tool_needed,
                                         machines_state[next_machines_possible[i] - 1])
                            next_machine_to_use = next_machines_possible[i]
                            break
                        elif next_machines_possible[i] == 4:
                            tool_changer(next_machines_possible[i], next_tool_needed,
                                         machines_state[next_machines_possible[i] - 1])
                            next_machine_to_use = next_machines_possible[i]
                            break
                elif machine_to_use == 1:
                    for i in range(len(next_machines_possible)):
                        if next_machines_possible[i] == 3:
                            tool_changer(next_machines_possible[i], next_tool_needed,
                                         machines_state[next_machines_possible[i] - 1])
                            next_machine_to_use = next_machines_possible[i]
                            break
                        elif next_machines_possible[i] == 4:
                            tool_changer(next_machines_possible[i], next_tool_needed,
                                         machines_state[next_machines_possible[i] - 1])
                            next_machine_to_use = next_machines_possible[i]
                            break
                elif machine_to_use == 3:
                    for i in range(len(next_machines_possible)):
                        if next_machines_possible[i] == 2:
                            tool_changer(next_machines_possible[i], next_tool_needed,
                                         machines_state[next_machines_possible[i] - 1])
                            next_machine_to_use = next_machines_possible[i]
                            break
                        elif next_machines_possible[i] == 1:
                            tool_changer(next_machines_possible[i], next_tool_needed,
                                         machines_state[next_machines_possible[i] - 1])
                            next_machine_to_use = next_machines_possible[i]
                            break
                elif machine_to_use == 4:
                    for i in range(len(next_machines_possible)):
                        if next_machines_possible[i] == 2:
                            tool_changer(next_machines_possible[i], next_tool_needed,
                                         machines_state[next_machines_possible[i] - 1])
                            next_machine_to_use = next_machines_possible[i]
                            break
                        elif next_machines_possible[i] == 1:
                            tool_changer(next_machines_possible[i], next_tool_needed,
                                         machines_state[next_machines_possible[i] - 1])
                            next_machine_to_use = next_machines_possible[i]
                            break
        elif type == 7:
            if first_iteration == 1:
                next_machine_to_use = 0
                machine_to_use = 0
                for i in range(len(machines_possible)):
                    if tool_needed == machines_state[machines_possible[i] - 1]:
                        machine_to_use = machines_possible[i]
                        break
                if machine_to_use == 0:
                    tool_changer(machines_possible[0], tool_needed, machines_state[machines_possible[0] - 1])
                    time.sleep(20)
                    machine_to_use = machines_possible[0]
            else:
                machine_to_use = next_machine_to_use
                next_machine_to_use = 0

            for i in range(len(next_machines_possible)):
                if next_tool_needed == machines_state[next_machines_possible[i] - 1] and next_machines_possible[
                    i] != machine_to_use:
                    if ((next_machines_possible[i] == 2 and machine_to_use == 1) or (
                            next_machines_possible[i] == 1 and machine_to_use == 2) or (
                            next_machines_possible[i] == 3 and machine_to_use == 4) or (
                            next_machines_possible[i] == 4 and machine_to_use == 3)):
                        next_machine_to_use = 0
                    else:
                        next_machine_to_use = next_machines_possible[i]
                        break

            if next_machine_to_use == 0:
                if machine_to_use == 2:
                    for i in range(len(next_machines_possible)):
                        if next_machines_possible[i] == 3:
                            tool_changer(next_machines_possible[i], next_tool_needed,
                                         machines_state[next_machines_possible[i] - 1])
                            next_machine_to_use = next_machines_possible[i]
                            break
                        elif next_machines_possible[i] == 4:
                            tool_changer(next_machines_possible[i], next_tool_needed,
                                         machines_state[next_machines_possible[i] - 1])
                            next_machine_to_use = next_machines_possible[i]
                            break
                elif machine_to_use == 1:
                    for i in range(len(next_machines_possible)):
                        if next_machines_possible[i] == 3:
                            tool_changer(next_machines_possible[i], next_tool_needed,
                                         machines_state[next_machines_possible[i] - 1])
                            next_machine_to_use = next_machines_possible[i]
                            break
                        elif next_machines_possible[i] == 4:
                            tool_changer(next_machines_possible[i], next_tool_needed,
                                         machines_state[next_machines_possible[i] - 1])
                            next_machine_to_use = next_machines_possible[i]
                            break
                elif machine_to_use == 3:
                    for i in range(len(next_machines_possible)):
                        if next_machines_possible[i] == 2:
                            tool_changer(next_machines_possible[i], next_tool_needed,
                                         machines_state[next_machines_possible[i] - 1])
                            next_machine_to_use = next_machines_possible[i]
                            break
                        elif next_machines_possible[i] == 1:
                            tool_changer(next_machines_possible[i], next_tool_needed,
                                         machines_state[next_machines_possible[i] - 1])
                            next_machine_to_use = next_machines_possible[i]
                            break
                elif machine_to_use == 4:
                    for i in range(len(next_machines_possible)):
                        if next_machines_possible[i] == 2:
                            tool_changer(next_machines_possible[i], next_tool_needed,
                                         machines_state[next_machines_possible[i] - 1])
                            next_machine_to_use = next_machines_possible[i]
                            break
                        elif next_machines_possible[i] == 1:
                            tool_changer(next_machines_possible[i], next_tool_needed,
                                         machines_state[next_machines_possible[i] - 1])
                            next_machine_to_use = next_machines_possible[i]
                            break
        elif type == 8:
            if first_iteration == 1:
                next_machine_to_use = 0
                machine_to_use = 0
                for i in range(len(machines_possible)):
                    if tool_needed == machines_state[machines_possible[i] - 1]:
                        machine_to_use = machines_possible[i]
                        break
                if machine_to_use == 0:
                    tool_changer(machines_possible[0], tool_needed, machines_state[machines_possible[0] - 1])
                    time.sleep(20)
                    machine_to_use = machines_possible[0]
            else:
                machine_to_use = next_machine_to_use
                next_machine_to_use = 0

            for i in range(len(next_machines_possible)):
                if next_tool_needed == machines_state[next_machines_possible[i] - 1] and next_machines_possible[
                    i] != machine_to_use:
                    if ((next_machines_possible[i] == 2 and machine_to_use == 1) or (
                            next_machines_possible[i] == 1 and machine_to_use == 2) or (
                            next_machines_possible[i] == 3 and machine_to_use == 4) or (
                            next_machines_possible[i] == 4 and machine_to_use == 3)):
                        next_machine_to_use = 0
                    else:
                        next_machine_to_use = next_machines_possible[i]
                        break

            if next_machine_to_use == 0:
                if machine_to_use == 2:
                    for i in range(len(next_machines_possible)):
                        if next_machines_possible[i] == 3:
                            tool_changer(next_machines_possible[i], next_tool_needed,
                                         machines_state[next_machines_possible[i] - 1])
                            next_machine_to_use = next_machines_possible[i]
                            break
                        elif next_machines_possible[i] == 4:
                            tool_changer(next_machines_possible[i], next_tool_needed,
                                         machines_state[next_machines_possible[i] - 1])
                            next_machine_to_use = next_machines_possible[i]
                            break
                elif machine_to_use == 1:
                    for i in range(len(next_machines_possible)):
                        if next_machines_possible[i] == 3:
                            tool_changer(next_machines_possible[i], next_tool_needed,
                                         machines_state[next_machines_possible[i] - 1])
                            next_machine_to_use = next_machines_possible[i]
                            break
                        elif next_machines_possible[i] == 4:
                            tool_changer(next_machines_possible[i], next_tool_needed,
                                         machines_state[next_machines_possible[i] - 1])
                            next_machine_to_use = next_machines_possible[i]
                            break
                elif machine_to_use == 3:
                    for i in range(len(next_machines_possible)):
                        if next_machines_possible[i] == 2:
                            tool_changer(next_machines_possible[i], next_tool_needed,
                                         machines_state[next_machines_possible[i] - 1])
                            next_machine_to_use = next_machines_possible[i]
                            break
                        elif next_machines_possible[i] == 1:
                            tool_changer(next_machines_possible[i], next_tool_needed,
                                         machines_state[next_machines_possible[i] - 1])
                            next_machine_to_use = next_machines_possible[i]
                            break
                elif machine_to_use == 4:
                    for i in range(len(next_machines_possible)):
                        if next_machines_possible[i] == 2:
                            tool_changer(next_machines_possible[i], next_tool_needed,
                                         machines_state[next_machines_possible[i] - 1])
                            next_machine_to_use = next_machines_possible[i]
                            break
                        elif next_machines_possible[i] == 1:
                            tool_changer(next_machines_possible[i], next_tool_needed,
                                         machines_state[next_machines_possible[i] - 1])
                            next_machine_to_use = next_machines_possible[i]
                            break
        elif type == 9:
            if first_iteration == 1:
                next_machine_to_use = 0
                machine_to_use = 0
                for i in range(len(machines_possible)):
                    if tool_needed == machines_state[machines_possible[i] - 1]:
                        machine_to_use = machines_possible[i]
                        break
                if machine_to_use == 0:
                    tool_changer(machines_possible[0], tool_needed, machines_state[machines_possible[0] - 1])
                    time.sleep(20)
                    machine_to_use = machines_possible[0]
            else:
                machine_to_use = next_machine_to_use
                next_machine_to_use = 0

            for i in range(len(next_machines_possible)):
                if next_tool_needed == machines_state[next_machines_possible[i] - 1] and next_machines_possible[
                    i] != machine_to_use:
                    if ((next_machines_possible[i] == 2 and machine_to_use == 1) or (
                            next_machines_possible[i] == 1 and machine_to_use == 2) or (
                            next_machines_possible[i] == 3 and machine_to_use == 4) or (
                            next_machines_possible[i] == 4 and machine_to_use == 3)):
                        next_machine_to_use = 0
                    else:
                        next_machine_to_use = next_machines_possible[i]
                        break

            if next_machine_to_use == 0:
                if machine_to_use == 2:
                    for i in range(len(next_machines_possible)):
                        if next_machines_possible[i] == 3:
                            tool_changer(next_machines_possible[i], next_tool_needed,
                                         machines_state[next_machines_possible[i] - 1])
                            next_machine_to_use = next_machines_possible[i]
                            break
                        elif next_machines_possible[i] == 4:
                            tool_changer(next_machines_possible[i], next_tool_needed,
                                         machines_state[next_machines_possible[i] - 1])
                            next_machine_to_use = next_machines_possible[i]
                            break
                elif machine_to_use == 1:
                    for i in range(len(next_machines_possible)):
                        if next_machines_possible[i] == 3:
                            tool_changer(next_machines_possible[i], next_tool_needed,
                                         machines_state[next_machines_possible[i] - 1])
                            next_machine_to_use = next_machines_possible[i]
                            break
                        elif next_machines_possible[i] == 4:
                            tool_changer(next_machines_possible[i], next_tool_needed,
                                         machines_state[next_machines_possible[i] - 1])
                            next_machine_to_use = next_machines_possible[i]
                            break
                elif machine_to_use == 3:
                    for i in range(len(next_machines_possible)):
                        if next_machines_possible[i] == 2:
                            tool_changer(next_machines_possible[i], next_tool_needed,
                                         machines_state[next_machines_possible[i] - 1])
                            next_machine_to_use = next_machines_possible[i]
                            break
                        elif next_machines_possible[i] == 1:
                            tool_changer(next_machines_possible[i], next_tool_needed,
                                         machines_state[next_machines_possible[i] - 1])
                            next_machine_to_use = next_machines_possible[i]
                            break
                elif machine_to_use == 4:
                    for i in range(len(next_machines_possible)):
                        if next_machines_possible[i] == 2:
                            tool_changer(next_machines_possible[i], next_tool_needed,
                                         machines_state[next_machines_possible[i] - 1])
                            next_machine_to_use = next_machines_possible[i]
                            break
                        elif next_machines_possible[i] == 1:
                            tool_changer(next_machines_possible[i], next_tool_needed,
                                         machines_state[next_machines_possible[i] - 1])
                            next_machine_to_use = next_machines_possible[i]
                            break

    elif id == 3:
        machine_to_use = next_machine_to_use
        next_machine_to_use = 0

    results = [machine_to_use, next_machine_to_use]
    return results


def update_database_P1_P2(increment, type):
    db = Database()
    stock = Stock()
    if type == 1:
        current = stock.read_Stock_P1()
        new = increment + current
    elif type == 2:
        current = stock.read_Stock_P2()
        new = increment + current

    db.close()


def make_on_m1(towrite, todo, c, p, time_needed, requests):
    string = "ns=4;s=|var|CODESYS Control Win V3 x64.Application.WH_M1_1.Piece"
    setting_an_int_variable(string, towrite)
    string = "ns=4;s=|var|CODESYS Control Win V3 x64.Application.Geral.M1.cmd_stop"
    setting_an_int_variable64(string, time_needed)
    string = "ns=4;s=|var|CODESYS Control Win V3 x64.Application.WH_M1_1.WH_M1"
    setting_a_variable_true(string)
    while True:
        string = "ns=4;s=|var|CODESYS Control Win V3 x64.Application.GVL.I[6]"
        sensor = get_variable(string)
        if sensor == True:
            break
    string = "ns=4;s=|var|CODESYS Control Win V3 x64.Application.Geral.M2.cmd_stop"
    setting_an_int_variable64(string, 0)
    while True:
        string = "ns=4;s=|var|CODESYS Control Win V3 x64.Application.GVL.I[6]"
        sensor = get_variable(string)
        if sensor == False:
            break
    string = "ns=4;s=|var|CODESYS Control Win V3 x64.Application.M1_M2.M1_M2"
    setting_a_variable_true(string)
    if todo == 'makeANDdeliver':
        while True:
            string = "ns=4;s=|var|CODESYS Control Win V3 x64.Application.GVL.I[1]"
            sensor = get_variable(string)
            if sensor == True:
                break
    status_decision(c, p, todo)


def make_on_m2(towrite, todo, c, p, time_needed, requests):
    string = "ns=4;s=|var|CODESYS Control Win V3 x64.Application.WH_M1_1.Piece"
    setting_an_int_variable(string, towrite)
    string = "ns=4;s=|var|CODESYS Control Win V3 x64.Application.Geral.M1.cmd_stop"
    setting_an_int_variable64(string, 0)
    string = "ns=4;s=|var|CODESYS Control Win V3 x64.Application.WH_M1_1.WH_M1"
    setting_a_variable_true(string)
    string = "ns=4;s=|var|CODESYS Control Win V3 x64.Application.Geral.M2.cmd_stop"
    setting_an_int_variable64(string, time_needed)
    string = "ns=4;s=|var|CODESYS Control Win V3 x64.Application.M1_M2.M1_M2"
    setting_a_variable_true(string)
    while True:
        string = "ns=4;s=|var|CODESYS Control Win V3 x64.Application.GVL.I[13]"
        sensor = get_variable(string)
        if sensor == True:
            break
    while True:
        string = "ns=4;s=|var|CODESYS Control Win V3 x64.Application.GVL.I[13]"
        sensor = get_variable(string)
        if sensor == False:
            break

    if todo == 'makeANDdeliver':
        while True:
            string = "ns=4;s=|var|CODESYS Control Win V3 x64.Application.GVL.I[1]"
            sensor = get_variable(string)
            if sensor == True:
                break
    status_decision(c, p, todo)


def make_on_m3(towrite, todo, c, p, time_needed, requests):
    string = "ns=4;s=|var|CODESYS Control Win V3 x64.Application.WH_M3.Piece"
    setting_an_int_variable(string, towrite)
    string = "ns=4;s=|var|CODESYS Control Win V3 x64.Application.Geral.M3.cmd_stop"
    setting_an_int_variable64(string, time_needed)
    string = "ns=4;s=|var|CODESYS Control Win V3 x64.Application.WH_M3.WH_M3"
    setting_a_variable_true(string)
    while True:
        string = "ns=4;s=|var|CODESYS Control Win V3 x64.Application.GVL.I[32]"
        sensor = get_variable(string)
        if sensor == True:
            break
    while True:
        string = "ns=4;s=|var|CODESYS Control Win V3 x64.Application.GVL.I[32]"
        sensor = get_variable(string)
        if sensor == False:
            break
    if todo == 'makeANDdeliver':
        while True:
            string = "ns=4;s=|var|CODESYS Control Win V3 x64.Application.GVL.I[1]"
            sensor = get_variable(string)
            if sensor == True:
                break
    status_decision(c, p, todo)


def make_on_m4(towrite, todo, c, p, time_needed, requests):
    string = "ns=4;s=|var|CODESYS Control Win V3 x64.Application.WH_M4.Piece"
    setting_an_int_variable(string, towrite)
    string = "ns=4;s=|var|CODESYS Control Win V3 x64.Application.Geral.M4.cmd_stop"
    setting_an_int_variable64(string, time_needed)
    string = "ns=4;s=|var|CODESYS Control Win V3 x64.Application.WH_M4.WH_M4"
    setting_a_variable_true(string)
    while True:
        string = "ns=4;s=|var|CODESYS Control Win V3 x64.Application.GVL.I[38]"
        sensor = get_variable(string)
        if sensor == True:
            break
    while True:
        string = "ns=4;s=|var|CODESYS Control Win V3 x64.Application.GVL.I[38]"
        sensor = get_variable(string)
        if sensor == False:
            break
    if todo == 'makeANDdeliver':
        while True:
            string = "ns=4;s=|var|CODESYS Control Win V3 x64.Application.GVL.I[1]"
            sensor = get_variable(string)
            if sensor == True:
                break
    status_decision(c, p, todo)


def switch_case(x, machine_number, todo, c, p1_quantity, p2_quantity, requests):
    import time
    c = c
    p = int(x[1:])
    if x == 'P1 and P2 restock':
        p1_time = p1_quantity * P1_RESTOCK_TIME
        p2_time = p2_quantity * P2_RESTOCK_TIME
        string1 = "ns=4;s=|var|CODESYS Control Win V3 x64.Application.P1_N1.Start"
        string2 = "ns=4;s=|var|CODESYS Control Win V3 x64.Application.P2_WH.Start"
        setting_a_variable_true(string1)
        setting_a_variable_true(string2)
        if p1_time >= p2_time:
            time.sleep(p2_time)
            setting_a_variable_false(string2)
            left = p1_time - p2_time
            time.sleep(left)
            setting_a_variable_false(string1)
        else:
            time.sleep(p1_time)
            setting_a_variable_false(string1)
            left = p2_time - p1_time
            time.sleep(left)
            setting_a_variable_false(string1)
        update_database_P1_P2(p1_quantity, 1)
        update_database_P1_P2(p2_quantity, 2)

    elif x == 'P1 restock':
        p1_time = p1_quantity * P1_RESTOCK_TIME
        string = "ns=4;s=|var|CODESYS Control Win V3 x64.Application.P1_N1.Start"
        setting_a_variable_true(string)
        time.sleep(p1_time)
        setting_a_variable_false(string)
        update_database_P1_P2(p1_quantity, 1)

    elif x == 'P2 restock':
        p2_time = p2_quantity * P2_RESTOCK_TIME
        string = "ns=4;s=|var|CODESYS Control Win V3 x64.Application.P1_N1.Start"
        setting_a_variable_true(string)
        time.sleep(p2_time)
        setting_a_variable_false(string)
        update_database_P1_P2(p2_quantity, 2)

    elif x == 'P3':
        towrite = 2
        update_database_P1_P2(-1, 2)
        time = 10
        if machine_number == 1:
            make_on_m1(towrite, todo, c, p, time, requests)
        elif machine_number == 3:
            make_on_m3(towrite, todo, c, p, time, requests)

    elif x == 'P4':
        towrite = 2
        update_database_P1_P2(-1, 2)
        time = 10
        if machine_number == 1:
            make_on_m1(towrite, todo, c, p, time, requests)
        elif machine_number == 2:
            make_on_m2(towrite, todo, c, p, time, requests)
        elif machine_number == 3:
            make_on_m3(towrite, todo, c, p, time, requests)
        elif machine_number == 4:
            make_on_m4(towrite, todo, c, p, time, requests)

    elif x == 'P5':
        towrite = 9
        time = 15
        if machine_number == 2:
            make_on_m2(towrite, todo, c, p, time, requests)
        elif machine_number == 3:
            make_on_m3(towrite, todo, c, p, time, requests)
        elif machine_number == 4:
            make_on_m4(towrite, todo, c, p, time, requests)

    elif x == 'P6':
        towrite = 1
        update_database_P1_P2(-1, 1)
        time = 20
        if machine_number == 1:
            make_on_m1(towrite, todo, c, p, time, requests)
        elif machine_number == 2:
            make_on_m2(towrite, todo, c, p, time, requests)
        elif machine_number == 4:
            make_on_m4(towrite, todo, c, p, time, requests)

    elif x == 'P7':
        towrite = 4
        time = 10
        if machine_number == 2:
            make_on_m2(towrite, todo, c, p, time, requests)
        elif machine_number == 3:
            make_on_m3(towrite, todo, c, p, time, requests)
        elif machine_number == 4:
            make_on_m4(towrite, todo, c, p, time, requests)

    elif x == 'P8':
        towrite = 6
        time = 30
        if machine_number == 1:
            make_on_m1(towrite, todo, c, p, time, requests)
        elif machine_number == 2:
            make_on_m2(towrite, todo, c, p, time, requests)
        elif machine_number == 3:
            make_on_m3(towrite, todo, c, p, time, requests)
        elif machine_number == 4:
            make_on_m4(towrite, todo, c, p, time, requests)

    elif x == 'P9':
        towrite = 7
        time = 10
        if machine_number == 1:
            make_on_m1(towrite, todo, c, p, time, requests)
        elif machine_number == 2:
            make_on_m2(towrite, todo, c, p, time, requests)
        elif machine_number == 3:
            make_on_m3(towrite, todo, c, p, time, requests)
        elif machine_number == 4:
            make_on_m4(towrite, todo, c, p, time, requests)


def setting_an_int_variable(string, towrite):
    towrite16 = int(towrite)
    var = client.get_node(string)
    variant = ua.Variant(towrite16, varianttype=ua.VariantType.Int16)
    data_value = ua.DataValue(variant)
    var.set_value(data_value)


def setting_an_int_variable64(string, towrite):
    towrite = int(towrite)
    towrite64 = np.int64(towrite)
    var = client.get_node(string)
    variant = ua.Variant(towrite64, varianttype=ua.VariantType.Int64)
    data_value = ua.DataValue(variant)
    var.set_value(data_value)


def setting_a_variable_true(string):
    var = client.get_node(string)
    var.set_value(True)


def setting_a_variable_false(string):
    var = client.get_node(string)
    var.set_value(False)


def get_variable(string):
    var = client.get_node(string)
    variable = var.get_value()
    return variable


def status_decision(c, p, todo):
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
        n = c[p - 3] + 1
        string = "ns=4;s=|var|CODESYS Control Win V3 x64.Application.WH_SH_PType.Piece_Type"
        setting_an_int_variable(string, p)
        string = "ns=4;s=|var|CODESYS Control Win V3 x64.Application.WH_SH_PType.Pieces_to_Shipp"
        setting_an_int_variable(string, n)
        show_terminal_shipping(p, n)
        string = "ns=4;s=|var|CODESYS Control Win V3 x64.Application.WH_SH_Control.Start"
        setting_a_variable_true(string)
        c[p - 3] = 0


def show_terminal(requests, id, time, init):
    print('-----------------------------------------------------------------------')
    title = pyfiglet.figlet_format('MES TERMINAL')
    title = colored(title, "blue")
    print(title)
    print('-----------------------------------------------------------------------')
    produced = id
    pending = 4 - produced
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
        string = '                             RESTOCK DAY'
        stringg = '          pieces P1 and P2 are being stored in the warehouse'
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
        if id == 0:
            if init == 1:
                print(f'{stringf1} P{workpiece_number[0]}{stringf5} About to start')
            elif init == 0:
                print(f'{stringf1} P{workpiece_number[0]}{stringf5} Making the piece')
            print(f'{stringf2} P{workpiece_number[1]}{stringf6} Waiting')
            print(f'{stringf3} P{workpiece_number[2]}{stringf5} Waiting')
            print(f'{stringf4} P{workpiece_number[3]}{stringf6} Waiting\n')
        elif id == 1:
            print(f'{stringf1} P{workpiece_number[0]}{stringf5} Done')
            print(f'{stringf2} P{workpiece_number[1]}{stringf6} Making the piece')
            print(f'{stringf3} P{workpiece_number[2]}{stringf5} Waiting')
            print(f'{stringf4} P{workpiece_number[3]}{stringf6} Waiting\n')
        elif id == 2:
            print(f'{stringf1} P{workpiece_number[0]}{stringf5} Done')
            print(f'{stringf2} P{workpiece_number[1]}{stringf6} Done')
            print(f'{stringf3} P{workpiece_number[2]}{stringf5} Making the piece')
            print(f'{stringf4} P{workpiece_number[3]} Waiting\n')
        elif id == 3:
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


def show_terminal_shipping(p, n):
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
    n = str(n)
    p = str(p)
    string = '                   Delivering ' + n
    string = string + " pieces of type P" + p
    stringf = colored(string, 'red', attrs=['bold'])
    print(f'{stringf}\n')

    print('-----------------------------------------------------------------------')


def is_new(old_list, new_list):
    # if not old_list and not new_list:
    #     # check if they are empty
    #     return True
    # if len(old_list) == 1 or len(new_list) == 1:
    #     # check if there is only one value
    #     return True
    if old_list is None and new_list is not None:
        # check if they are not None
        return True
    elif new_list is None:
        return False
    # check if they are different
    for new_msg in new_list:
        if new_msg not in old_list:
            return True
    return False


def get_tool(piece_type):
    p = int(piece_type[1:])
    pecas_tools = [2, 3, 4, 1, 4, 3, 3]

    return pecas_tools[p - 3]


def search_for_order_id(dict_list):
    for d in dict_list:
        if "order_id" in d:
            return True
    return False


def search_for_restock_order(dict_list):
    for d in dict_list:
        if d["workpiece"] in (P1_RESTOCK_STR, P2_RESTOCK_STR, P1_AND_P2_RESTOCK_STR):
            return True
    return False


def update_arrival_date_for_all_orders(current_day):
    for order_num in stats.read_All_Order_Numbers():
        order_num = remove_whitespace(order_num)
        stats.update_ad(order_num, current_day)


def remove_whitespace(string):
    return ''.join(string.split())


def cycle_through_msg_to_get_id(message):
    for dic in message:
        if "order_id" in dic:
            return remove_whitespace(dic['order_id'])
        else:
            pass


def list_to_dict(lst):
    result = {}
    for item in lst:
        pairs = item.split(';')
        for pair in pairs:
            key, value = pair.strip().split(':')
            result[key] = value.strip()
    return result


def conclude_order(local_order_id: str, current_day):
    # orders_obj = Orders()
    # conclude_obj = Concluded()
    # stats = Statistics()
    order = orders_obj.read_Order_Number_X(local_order_id)
    order_dic = list_to_dict(order)
    number = order_dic['number']
    work_piece = order_dic['workpiece']
    quantity = order_dic['quantity']
    due_date = order_dic['duedate']
    late_pen = order_dic['latepen']
    early_pen = order_dic['earlypen']
    client_id = order_dic['clientid']
    conclude_obj.add_Concluded(number,
                               work_piece,
                               quantity,
                               due_date,
                               late_pen,
                               early_pen,
                               client_id)
    stats.update_dd(local_order_id, current_day)
    orders_obj.delete_Order(number, client_id)


if __name__ == '__main__':

    # Connect to server
    url = "opc.tcp://localhost:4840"
    client = Client(url)
    client.connect()
    c=[0,0,0,0,0,0,0] #peças em armazem
    maquina=[0,0]

    comm_to_erp = ThreadedServer()
    comm_to_erp.start()
    old_msg = comm_to_erp.get_message()
    day_cnt = 0

    message_received = False
    while True:
        message = comm_to_erp.get_message()
        if message is not None:
            if not message_received:
                message_received = True
                print(f"Got a new message from the ERP {message}")
                day_cnt += 1
                print()
                if search_for_order_id(message):
                    # order is to be concluded today
                    # move order from the orders schematic to the concluded
                    # update dispatch day
                    order_id = cycle_through_msg_to_get_id(message)
                    conclude_order(order_id, day_cnt)
                if search_for_restock_order(message):
                    # update the arrival date for all orders
                    update_arrival_date_for_all_orders(day_cnt)
                    # TODO in the future make this dynamic...

                requests=message
                size = len(requests)
                id = 0
                first_iteration = 1
                show_terminal(requests, id, 0, 1)
                a = time.time()

                for id in range(size):
                    show_terminal(requests, id, 0, 0)
                    string = requests[id]['workpiece']
                    todo = requests[id]['status']
                    p1_quantity = requests[id]['p1_amount']
                    p2_quantity = requests[id]['p2_amount']

                    if id == 3:
                        next_string = '0'
                    else:
                        next_string = requests[id + 1]['workpiece']

                    if todo != 0:
                        aux = machine_decision(string, next_string, machines_state, first_iteration, id, maquina[1], client)
                        maquina = aux
                        machines_state[maquina[0]-1]=get_tool(string)
                        first_iteration = 0
                    else:
                        maquina = 0
                    print(f'about to make a piece on machine {maquina[0]}')
                    switch_case(string, maquina[0], todo, c, p1_quantity, p2_quantity, requests)
                    print('piece done')
                    b = time.time()
                    b = b - a
                    show_terminal_end(requests, b)
        else:
            message_received = False
"""


requests = [{'workpiece': 'P6', 'status': 'store2deliver', 'p1_amount': '0', 'p2_amount': '0'},
            {'workpiece': 'P6', 'status': 'store2deliver', 'p1_amount': '0', 'p2_amount': '0'},
            {'workpiece': 'P6', 'status': 'store2deliver', 'p1_amount': '0', 'p2_amount': '0'},
            {'workpiece': 'P6', 'status': 'makeANDdeliver', 'p1_amount': '0', 'p2_amount': '0'}]


size = len(requests)
print(f'size={size}')
id = 0
first_iteration = 1
#show_terminal(requests, id, 0, 1)
a = time.time()

for id in range(size):
    #show_terminal(requests, id, 0, 0)
    string = requests[id]['workpiece']
    todo = requests[id]['status']
    p1_quantity = requests[id]['p1_amount']
    p2_quantity = requests[id]['p2_amount']

    if id == 3:
        next_string = '0'
    else:
        next_string = requests[id + 1]['workpiece']

    if todo != 0:
        aux = machine_decision(string, next_string, machines_state, first_iteration, id, maquina[1], client)
        maquina = aux
        machines_state[maquina[0] - 1] = get_tool(string)
        first_iteration = 0
    else:
        maquina = 0
    print(f'about to make a piece on machine {maquina[0]}')
    switch_case(string, maquina[0], todo, c, p1_quantity, p2_quantity, requests)
    print('piece done')
    #b = time.time()
    #b = b - a
    #show_terminal_end(requests, b)
    """
