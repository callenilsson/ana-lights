import time
from neopixel import *
import numpy as np
import math
import random
import socket
import json
import numpy as np
import time
import zlib
import skvideo.io

def applyNumpyColors(strip, frame):
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, Color(int(frame[i][0][1]), int(frame[i][0][0]), int(frame[i][0][2])))
    strip.show()

def colorWipe(strip):
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, Color(0,0,0))
    strip.show()

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

    strip1 = Adafruit_NeoPixel(144, 12, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, 0)
    strip2 = Adafruit_NeoPixel(144, 18, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, 0)
    strip3 = Adafruit_NeoPixel(288, 13, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, 1)
    strip4 = Adafruit_NeoPixel(288, 19, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, 1)
    strip1.begin()
    strip2.begin()
    strip3.begin()
    strip4.begin()

    print('Loading video...')
    video = skvideo.io.vread('videos/cloudless_lights_3.avi')[:, :288]
    video = video*0.1
    video = video.astype(np.uint8)
    fps = 60

    server = socket.socket()
    server.bind(('192.168.0.197', 9090))
    server.listen(1)
    print('Ready')
    conn, client_address = server.accept()

    recv_song_start_time = float(conn.recv(1024).decode())
    msg = 'RPi 3 ready to start at ' + str(recv_song_start_time)
    conn.send(msg.encode())

    recv_time = float(conn.recv(1024).decode())
    start_time = time.time()
    time_diff = recv_time - start_time
    start_time = start_time - time_diff

    while True:
        try:
            t = time.time()
            true_index = int((time.time() - start_time + recv_song_start_time)*fps)
            print(time.time() - start_time + recv_song_start_time, true_index)
            frame = video[true_index]

            applyNumpyColors(strip1, frame)
            applyNumpyColors(strip2, frame)
            applyNumpyColors(strip3, frame)
            applyNumpyColors(strip4, frame)

            print(int(1/(time.time() - t)), 'fps')
        except:
            colorWipe(strip1)
            colorWipe(strip2)
            colorWipe(strip3)
            colorWipe(strip4)
            exit()
