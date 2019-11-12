import socket
import time
import json
import matplotlib.pyplot as plt
import numpy as np
import zlib
import cv2
import mss
import pickle

def Color(red, green, blue, white=0):
    """Convert the provided red, green, blue color to a 24-bit color value.
    Each color component should be a value 0-255 where 0 is the lowest intensity
    and 255 is the highest intensity.
    """
    return (white << 24) | (red << 16) | (green << 8) | blue

rpi = socket.socket()
rpi.connect(('192.168.0.152', 9090))

mon = {'top' : 620, 'left' : 1400, 'width' : 1000, 'height' : 288}
sct = mss.mss()
while True:
    t = time.time()

    img = np.asarray(sct.grab(mon))[:,:,:3]
    img = cv2.resize(img, dsize=(10, 288), interpolation=cv2.INTER_NEAREST)[:,0,:]

    img_color = []
    for i in range(len(img)):
        img_color.append(Color(int(img[i,1]), int(img[i,2]), int(img[i,0])))

    data = pickle.dumps(img_color)
    rpi.send(data)
    rpi.recv(1024).decode()

    print(int(1/(time.time()-t)), 'fps')
