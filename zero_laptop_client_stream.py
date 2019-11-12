import socket
import time
import json
import matplotlib.pyplot as plt
import numpy as np
import zlib
import cv2
import mss
import pickle

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

rpi = socket.socket()
rpi.connect(('192.168.0.152', 9090))

mon = {'top' : 620, 'left' : 1400, 'width' : 1000, 'height' : 288}
sct = mss.mss()
while True:
    t = time.time()

    img = np.asarray(sct.grab(mon))[:,:,:3]
    img = cv2.resize(img, dsize=(10, 288), interpolation=cv2.INTER_NEAREST)

    #data = json.dumps(img.tolist()).encode()
    #data = pickle.dumps(img)
    #data = zlib.compress(data)
    #data_size = intToBytes(len(data)) # 4 bytes
    #rpi.sendall(data_size)
    #rpi.sendall(data)
    data = zlib.compress(pickle.dumps(img))
    print(len(data))
    rpi.send(data)
    print(rpi.recv(1024).decode())

    # data = rpi.recv(4)
    # next1 = bytesToInt(data)
    # if not(next1 == 1):
    #     exit()

    #delta = time.time()-t
    #if delta < 1/60.0:
    #    time.sleep(1/60.0 - (delta))
    #print(t)
    #print(int(1/(time.time()-t)), 'fps')
