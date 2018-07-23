#!/usr/bin/env python3

import zmq
from time import sleep
import signal

def sigint_handler(signal, stackFram):
    global endProgram
    endProgram = True

signal.signal(signal.SIGINT, sigint_handler)
context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.connect("tcp://127.0.0.1:9000")
accelFilter = ""
socket.setsockopt_string(zmq.SUBSCRIBE, accelFilter)

poller = zmq.Poller()
poller.register(socket,zmq.POLLIN)


endProgram = False
while endProgram == False:
    #events = dict(poller.poll())
    socket.poll(flags=zmq.POLLIN)
#    for event in events:
#        print("%s %s\n" % (event, events[event]))
    try:
        string = socket.recv_string(zmq.NOBLOCK)
    except Exception as e:
        print("Error %s" % e)
        sleep(1)
    else: print("%s" % string)

