import ctypes
import ctypes.util
from datetime import datetime
import hashlib
import pathlib
import os
import time


CLOCK_REALTIME = 0
configFile = 'config.ini'


class timespec(ctypes.Structure):
    _fields_ = [('tv_sec', ctypes.c_long), ('tv_nsec', ctypes.c_long)]
librt = ctypes.CDLL(ctypes.util.find_library("rt"))
clock_gettime = librt.clock_gettime
clock_gettime.argtypes = [ctypes.c_int, ctypes.POINTER(timespec)]


def now():
    ts = timespec()
    if clock_gettime(CLOCK_REALTIME , ctypes.pointer(ts)) != 0:
        errno_ = ctypes.get_errno()
        raise OSError(errno_, os.strerror(errno_))
    return ts.tv_sec + ts.tv_nsec * 1e-9

def setNow(newNow):
    ts = timespec()
    ts.tv_sec = int(time.mktime(newNow.timetuple()))
    ts.tv_nsec = 0
    librt.clock_settime(CLOCK_REALTIME, ctypes.byref(ts))

def newFile(dir, name):
    mkdir_p(dir)
    return open(dir + '/' + name.format(now()), 'w', encoding="utf-8")

def moveFile(f, dir):
    f.close()
    mkdir_p(dir)
    os.rename(f.name, dir + '/' + os.path.basename(f.name))

def mkdir_p(dir):
    pathlib.Path(dir).mkdir(parents=True, exist_ok=True)

def exists(file):
    return os.path.exists(file)

def flatMap(list, dict):
    """
    Takes a list of key and returns a mapped list to the values in dict
    if the key is invalid, it is ignored
    """
    result = []
    for key in list:
        try:
            value = dict[key]
            result.append(value)
        except KeyError as err:
            continue
    return result

def md5(string):
    return hashlib.md5(string.encode('utf-8')).hexdigest()

