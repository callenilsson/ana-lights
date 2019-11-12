import socket
import time
import json
import matplotlib.pyplot as plt
import numpy as np
import zlib
import cv2
import mss
import pickle

rpi = socket.socket()
rpi.connect(('192.168.0.152', 9090))

mon = {'top' : 620, 'left' : 1400, 'width' : 1000, 'height' : 288}
sct = mss.mss()
while True:
    t = time.time()

    img = np.asarray(sct.grab(mon))[:,:,:3]
    img = cv2.resize(img, dsize=(10, 288), interpolation=cv2.INTER_NEAREST)[:,0,:]

    data = pickle.dumps(img)
    rpi.send(data)
    rpi.recv(1024).decode()

    print(int(1/(time.time()-t)), 'fps')
