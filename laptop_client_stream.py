import socket
import time
import json
import matplotlib.pyplot as plt
import numpy as np
import zlib
import cv2
import mss

def intToBytes(n):
    b = bytearray([0, 0, 0, 0])   # init
    b[3] = n & 0xFF
    n >>= 8
    b[2] = n & 0xFF
    n >>= 8
    b[1] = n & 0xFF
    n >>= 8
    b[0] = n & 0xFF
    return b

def bytesToInt(b):
    n = (b[0]<<24) + (b[1]<<16) + (b[2]<<8) + b[3]
    return n

rpi1 = socket.socket()
rpi2 = socket.socket()
#rpi3 = socket.socket()
rpi1.connect(('192.168.0.150', 9090))
rpi2.connect(('192.168.0.179', 9090))
#rpi3.connect(('192.168.0.197', 9090))

mon = {'top' : 590, 'left' : 1158, 'width' : 998, 'height' : 298}
sct = mss.mss()
while True:
    t = time.time()

    img = np.asarray(sct.grab(mon))[:,:,:3]
    img = cv2.resize(img, dsize=(10, 288), interpolation=cv2.INTER_NEAREST)

    data = json.dumps(img.tolist()).encode()
    data = zlib.compress(data)
    data_size = intToBytes(len(data)) # 4 bytes

    rpi1.sendall(data_size)
    rpi2.sendall(data_size)
    #rpi3.sendall(data_size)
    rpi1.sendall(data)
    rpi2.sendall(data)
    #rpi3.sendall(data)

    data1 = rpi1.recv(4)
    data2 = rpi2.recv(4)
    #data3 = rpi3.recv(4)
    next1 = bytesToInt(data1)
    next2 = bytesToInt(data2)
    #next3 = bytesToInt(data3)
    if not(next1 == 1 or next2 == 1): #or next3 == 1):
        exit()


    delta = time.time()-t
    if delta < 1/60.0:
        time.sleep(1/60.0 - (delta))
    #print(int(1/(time.time()-t)), 'fps').
