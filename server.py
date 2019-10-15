import socket
import numpy as np
import skvideo.io
import time
from neopixel import *
import math
from scipy import ndimage
import scipy.misc
import random

def bytesToInt(b):
    b = bytearray(b)
    n = (b[0]<<24) + (b[1]<<16) + (b[2]<<8) + b[3]
    return n

def applyNumpyColors(strip, frame):
    for i in range(strip.numPixels()):
        frame = np.clip(frame,0,255)
        strip.setPixelColor(i, Color(int(round(frame[i,1])), int(round(frame[i,0])), int(round(frame[i,2]))))
    strip.show()

def colorWipe():
    global strip, LED_COUNT, start_time
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, Color(0,0,0))
    strip.show()

if __name__ == '__main__':
    global LED_COUNT, renders, remainder, fps
    # LED strip configuration:
    LED_COUNT      = 144      # Number of LED pixels.
    LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
    #LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
    LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
    LED_DMA        = 10      # DMA channel to use for generating signal (try 10)
    LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
    LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
    LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53

    strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
    strip.begin()

    print('Waiting for client...')
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.bind(('192.168.0.150', 8089))
    serversocket.listen(5)
    conn, address = serversocket.accept()

    try:
        print('Starting strip stream...')
        while True:
            data = conn.recv(4)
            length = bytesToInt(data)
            data = conn.recv(length)
            while len(data) < length:
                data += conn.recv(length - len(data))
            np_strip = np.fromstring(data, dtype=np.float64).reshape((144,3))

            applyNumpyColors(strip, np_strip)

    except KeyboardInterrupt:
        colorWipe()
