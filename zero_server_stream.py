import time
from rpi_ws281x import *
import numpy as np
import math
import random
import socket
import json
import numpy as np
import time
import zlib
import pickle

def applyNumpyColors(strip, frame):
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, Color(int(frame[i][0][1]), int(frame[i][0][2]), int(frame[i][0][0])))
    strip.show()

def colorWipe(strip):
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, Color(0,0,0))
    strip.show()

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

def recv_all(conn, size):
    data = conn.recv(size)
    while len(data) < size:
        diff = size - len(data)
        data += conn.recv(diff)
        #print('HEJ')
    return data

if __name__ == '__main__':
    # LED strip configuration:
    LED_COUNT      = 144      # Number of LED pixels.
    LED_PIN        = 17      # GPIO pin connected to the pixels (18 uses PWM!).
    #LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
    LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
    LED_DMA        = 10      # DMA channel to use for generating signal (try 10)
    LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
    LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
    LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53

    strip = Adafruit_NeoPixel(288, 13, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, 1)
    strip.begin()

    print('ready')

    server = socket.socket()
    server.bind(('0.0.0.0', 9090))
    server.listen(1)
    conn, client_address = server.accept()

    HEADERSIZE = 10

    while True:
        try:
            full_msg = b''
            new_msg = True
            while True:
                msg = conn.recv(16)
                if new_msg:
                    print("new msg len:",msg[:HEADERSIZE])
                    msglen = int(msg[:HEADERSIZE])
                    new_msg = False

                print(f"full message length: {msglen}")

                full_msg += msg

                print(len(full_msg))

                if len(full_msg)-HEADERSIZE == msglen:
                    print("full msg recvd")
                    print(full_msg[HEADERSIZE:])
                    print(pickle.loads(full_msg[HEADERSIZE:]))
                    new_msg = True
                    full_msg = b""



            # t1 = time.time()
            # data = conn.recv(4)
            # t2 = time.time()
            # data_size = bytesToInt(data)
            # t3 = time.time()
            # data = recv_all(conn, data_size)
            # t4 = time.time()
            # data = zlib.decompress(data)
            # t5 = time.time()
            # data = data.decode()
            # t6 = time.time()
            # print(data)
            # print(len(data))
            # #frame = json.loads(data)
            # frame = pickle.loads(data)
            # t7 = time.time()

            # applyNumpyColors(strip, frame)
            # t8 = time.time()

            # conn.sendall(intToBytes(1))
            # t9 = time.time()
            # print(t2-t1, t3-t2, t4-t3, t5-t4, t6-t5, t7-t6, t8-t7, t9-t8, '\n')
            # #print(int(1/(time.time()-t)), 'fps')
        except Exception as e:
            print(e)
            colorWipe(strip)
            exit()
