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

client = socket.socket()
#client.connect(('192.168.1.129', 44446))
#client.connect(('192.168.1.147', 44446))
client.connect(('192.168.0.150', 9090))

mon = {'top' : 590, 'left' : 1158, 'width' : 998, 'height' : 298}
sct = mss.mss()
while True:
    t = time.time()

    img = np.asarray(sct.grab(mon))[:,:,:3]
    img = cv2.resize(img, dsize=(10, 288), interpolation=cv2.INTER_NEAREST)

    data = json.dumps(img.tolist()).encode()
    data = zlib.compress(data)
    data_size = intToBytes(len(data)) # 4 bytes
    client.sendall(data_size)
    client.sendall(data)

    data = client.recv(4)
    next = bytesToInt(data)
    if not(next == 1):
        exit()


    delta = time.time()-t
    if delta < 1/60.0:
        time.sleep(1/60.0 - (delta))
    #print(int(1/(time.time()-t)), 'fps').
