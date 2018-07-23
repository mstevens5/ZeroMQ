#!/usr/bin/env python3

import threading

endProgram = False

def sigint_handler(signal, stackFrame):
    global endProgram
    endProgram = True

def recv_raw_data(name, port, filename):
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect("tcp://127.0.0.1:" + port)
    subFilter = ""
    socket.setsockopt_string(zmq.SUBSCRIBE, subFilter)
    
    while endProgram == False:
        socket.poll(flags=zmq.POLLIN)
        try:
            string = socket.recv_string(zmq.NOBLOCK)
        except Exception as e:
            print("Error %s" % e)
        else:
            print("%s" % string)

if __name__ == "__main__":
    t = threading.Thread(target=recv_raw_data, args=("Accelerometer","9000","accel:{.3f}"))
    t.start()
    t.join()
