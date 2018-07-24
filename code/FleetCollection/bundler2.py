#!/usr/bin/env python3

import threading
import zmq
import signal

import configparser
import os

endProgram = False

configFile = 'config.ini'

def exists(file):
    return os.path.exists(file)

def sigint_handler(signal, stackFrame):
    global endProgram
    endProgram = True

def recv_raw_data(name, port, filename):
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect("tcp://127.0.0.1:" + port)
    subFilter = ""
    socket.setsockopt_string(zmq.SUBSCRIBE, subFilter)

    print("name %s, port %s, filename %s" % (name, port, filename))

    while endProgram == False:
        socket.poll(timeout=2500, flags=zmq.POLLIN)
        try:
            string = socket.recv_string(zmq.NOBLOCK)
        except Exception as e:
            print("Name: %s, Error: %s" % (name,e))
        else:
            print("%s" % string)

if __name__ == "__main__":
    if not exists(configFile):
        print("Missing file: {}".format(configFile))
        exit(1)

    config = configparser.ConfigParser()
    config.read(configFile)
    try:
        progs = config['bundle_creator']['sub_programs']
        progs = [x.strip() for x in progs.split(',')]
        subProgs = []
        for prog in progs:
            subProgs.append(
                {'name': prog,
                'port': config[prog]['publisher_port'],
                'filename': config[prog]['file_name']
                })
    except KeyError as err:
        print("Missing key: {}".format(err))
        exit(1)

    signal.signal(signal.SIGINT, sigint_handler)
    threads = []
    for prog in subProgs:
        print("%s %s %s" % (prog['name'], prog['port'], prog['filename']))
        threads.append(threading.Thread(target=recv_raw_data, 
            args=(prog['name'], prog['port'], 
            prog['filename'])
            ))
        threads[-1].start()
    
    for t in threads:
        t.join()
