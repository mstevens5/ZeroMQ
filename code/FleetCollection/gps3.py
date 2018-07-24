#!/usr/bin/env python3

import os
import zmq
import time

import configparser
import signal
from sys import exit
from time import sleep

configFile = 'config.ini'

def exists(file):
    return os.path.exists(file)

if __name__ == "__main__":
    if not exists(configFile):
        print('Missing file: {}'.format(configFile))
        exit(1)

    config = configparser.ConfigParser()
    config.read(configFile)
    try:
        workDir = config['general']['working_dir']
        doneDir = config['general']['done_dir']
        interval = int(config['general']['read_interval'])
        splitSignal = config['general']['split_signal']
        name = config['gps']['file_name']
        pubPort = config['gps']['publisher_port']#
    except KeyError as err:
        print('Missing key: {}'.format(err))
        exit(1)

    def kill_handler(signal, stackFrame):
        global shouldEndFile
        global shouldStop
        shouldEndFile = True
        shouldStop = True
    signal.signal(signal.SIGTERM, kill_handler)
    signal.signal(signal.SIGINT, kill_handler)

    def split_handler(signal, stackFrame):
        global shouldEndFile
        shouldEndFile = True
    signal.signal(signal.Signals[splitSignal], split_handler)

    # Start publisher
    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    socket.bind("tcp://127.0.0.1:" + pubPort)

    shouldStop = False

    axes = {'x': 500.55, 'y':1000.1010, 'z':1500.1515}
    while True:
        if shouldStop:
            exit(0)
        msg = '{:.3f},{:f},{:f},{:f}\n'.format(time.time(), axes['x'], axes['y'], axes['z'])
        print("Before send: %s" % msg)
        #socket.send_string(msg)
        socket.send_string("FROM GPS")
        print("After send: %s" % msg)
        sleep(interval)
