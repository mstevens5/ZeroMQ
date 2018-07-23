#!/usr/bin/env python3

import adxl
from common import *

import configparser
import signal
from sys import exit
from time import sleep

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
        name = config['accelerometer']['file_name']
        pubPort = config['accelerometer']['publisher_port']#
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

    adxl345 = adxl.ADXL345()
    f = newFile(workDir, name)
    shouldEndFile = False
    shouldStop = False

    while True:
        if shouldEndFile:
            shouldEndFile = False
            moveFile(f, doneDir)
            if shouldStop:
                exit(0)
            f = newFile(workDir, name)

        axes = adxl345.getAxes()
        f.write('{:.3f},{:f},{:f},{:f}\n'.format(now(), axes['x'], axes['y'], axes['z']))
        f.flush()

        sleep(interval)
