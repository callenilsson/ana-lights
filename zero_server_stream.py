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

    while True:
        try:
            t = time.time()
            data = conn.recv(4)
            data_size = bytesToInt(data)
            data = recv_all(conn, data_size)
            data = zlib.decompress(data)
            frame = json.loads(data.decode())

            applyNumpyColors(strip, frame)

            conn.sendall(intToBytes(1))
            print(int(1/(time.time()-t)), 'fps')
        except Exception as e:
            print(e)
            colorWipe(strip)
            exit()
