#!/usr/bin/env python3

import zmq
from time import sleep
import signal

def sigint_handler(signal, stackFrame):
    global endProgram
    endProgram = True

signal.signal(signal.SIGINT, sigint_handler)
context = zmq.Context()
socket = context.socket(zmq.PUB)
#socket.connect("ipc://domainsock")
#socket.connect("tcp://127.0.0.1:9000")
socket.bind("tcp://127.0.0.1:9000")
f = open('accel.out', 'w')
count = 0
endProgram = False
while not endProgram:
    data = 'Accel-' + str(count) + '\n'
    f.write(data)
    f.flush()
    socket.send_string(data)
    sleep(0.3)
    count += 1
f.close()
