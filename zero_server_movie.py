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
import skvideo.io
import threading
import pickle as p

def applyNumpyColors(strip, frame):
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, int(frame[i]))
    strip.show()

def colorWipe(strip):
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, Color(0,0,0))
    strip.show()

def lights_thread(lock, barrier, strip, video, video_ending):
    global action, diff_time, start_time, user_start_time, ending_start_time
    barrier.wait()
    hej = 0
    while True:
        with lock:
            get_action = str(action)

        if get_action == 'start':
            try:
                t = time.time()
                true_index = int((time.time()+diff_time - start_time + user_start_time)*fps)
                frame = video[true_index]
                applyNumpyColors(strip, frame)
                hej = int(1/(time.time() - t))
                #print(int(1/(time.time() - t)), 'fps')
            except:
                with lock:
                    action = 'stop'

        elif get_action == 'stop':
            print(hej, 'fps')
            colorWipe(strip)
            barrier.wait()

        elif get_action == 'pause':
            barrier.wait()

        if get_action == 'ending':
            try:
                #t = time.time()
                true_index = int((time.time()-diff_time - ending_start_time)*fps)
                frame = video_ending[true_index]
                applyNumpyColors(strip, frame)
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

    # strip = Adafruit_NeoPixel(288, 13, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, 1)
    # strip.begin()

    # print('Loading video...')
    # video = np.load('lights/ana_lights_gbg.npy')
    # video_ending = np.load('lights/ana_ending.npy')
    # fps = 30

    server = socket.socket()
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('0.0.0.0', 9091))
    server.listen(1)
    print('Ready')
    conn, client_address = server.accept()

    global action, diff_time, start_time, user_start_time, ending_start_time
    # Get laptop time to sync time difference
    laptop_time = float(conn.recv(1024).decode())
    pi_time = time.time()
    diff_time = laptop_time - pi_time
    print(diff_time)
    server.close()
    exit()

    lock = threading.Lock()
    barrier = threading.Barrier(2)
    
    action = 'stop'
    threading.Thread(target=lights_thread, args=(lock, barrier, strip, video, video_ending)).start()

    while True:
        action_recv = conn.recv(1024).decode()
        if action_recv == 'start':
            with lock:
                user_start_time = float(conn.recv(1024).decode())
                msg = 'RPi Zero ready to start at ' + str(user_start_time)
                conn.send(msg.encode())
                start_time = float(conn.recv(1024).decode())
                if action == 'stop' or action == 'pause':
                    action = 'start'
                    barrier.wait()
                else:
                    action = 'start'

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
                ending_start_time = time.time()
                if action == 'stop' or action == 'pause':
                    action = 'ending'
                    barrier.wait()
                else:
                    action = 'ending'