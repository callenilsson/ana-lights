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
import threading

def applyNumpyColors(strip, frame):
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, Color(int(frame[i][0][1]), int(frame[i][0][0]), int(frame[i][0][2])))
    strip.show()

def colorWipe(strip):
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, Color(0,0,0))
    strip.show()

def lights_thread(lock, barrier, strips, video, video_ending):
    global action, start_time, user_start_time, ending_start_time
    barrier.wait()
    while True:
        with lock:
            get_action = str(action)

        if get_action == 'start':
            try:
                #t = time.time()
                true_index = int((time.time() - start_time + user_start_time)*fps)
                frame = video[true_index]
                for strip in strips: applyNumpyColors(strip, frame)
                #print(int(1/(time.time() - t)), 'fps')
            except:
                with lock:
                    action = 'stop'

        elif get_action == 'stop':
            for strip in strips: colorWipe(strip)
            barrier.wait()

        elif get_action == 'pause':
            barrier.wait()

        if get_action == 'ending':
            try:
                #t = time.time()
                true_index = int((time.time() - ending_start_time)*fps)
                frame = video_ending[true_index]
                for strip in strips: applyNumpyColors(strip, frame)
                #print(int(1/(time.time() - t)), 'fps')
            except:
                with lock:
                    action = 'stop'

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
    strips = [strip1, strip2, strip3, strip4]

    print('Loading video...')
    video = np.load('lights/ana_lights_gbg.npy')
    video_ending = np.load('lights/ana_ending.npy')
    fps = 30

    server = socket.socket()
    server.bind(('0.0.0.0', 9090))
    server.listen(1)
    print('Ready')
    conn, client_address = server.accept()

    lock = threading.Lock()
    barrier = threading.Barrier(2)
    global action, start_time, user_start_time, ending_start_time
    threading.Thread(target=lights_thread, args=(lock, barrier, strips, video, video_ending)).start()

    while True:
        action_recv = conn.recv(1024).decode()
        if action_recv == 'start':
            with lock:
                user_start_time = float(conn.recv(1024).decode())
                msg = 'RPi 3 ready to start at ' + str(user_start_time)
                conn.send(msg.encode())
                wait_to_start = conn.recv(1024).decode()
                start_time = time.time()
                action = 'start'
                barrier.wait()

        elif action_recv == 'stop':
            with lock:
                action = 'stop'

        elif action_recv == 'pause':
            with lock:
                action = 'pause'

        elif action_recv == 'resume':
            with lock:
                action = 'start'
                barrier.wait()

        elif action_recv == 'ending':
            with lock:
                action = 'ending'
                ending_start_time = time.time()
                barrier.wait()