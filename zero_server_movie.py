import time
from neopixel import *
import socket
import numpy as np
import threading
import ntplib
import json
import pickle

def applyNumpyColors(strip, frame):
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, frame[i])
    strip.show()

def colorWipe(strip):
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, Color(0,0,0))
    strip.show()

def stripStatus(strip, color):
    colorWipe(strip)
    for i in range(10):
        strip.setPixelColor(int(i*strip.numPixels()/10), Color(color[0], color[1], color[2]))
    strip.show()

def mapSelect(strip, color):
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, Color(color[0], color[1], color[2]))
    strip.show()

def lights_thread(lock, barrier, strip, video, video_ending):
    global action, diff_time, initial_offset, start_time, ending_start_time, client, offset, stream_data
    barrier.wait()
    hej = 0
    while True:
        with lock:
            get_action = str(action)

        if get_action == 'start':
            try:
                t = time.time()
                with lock:
                    true_index = int(abs((get_laptop_time() - start_time)*fps))
                frame = video[true_index].tolist()
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

        elif get_action == 'ready':
            colorWipe(strip)
            stripStatus(strip, [10,0,0])
            barrier.wait()

        elif get_action == 'pause':
            barrier.wait()

        if get_action == 'ending':
            try:
                #t = time.time()
                true_index = int(abs((get_laptop_time() - ending_start_time)*fps))
                frame = video_ending[true_index].tolist()
                applyNumpyColors(strip, frame)
                #print(int(1/(time.time() - t)), 'fps')
            except:
                with lock:
                    action = 'stop'

        if get_action == 'map_select':
            mapSelect(strip, [10,10,10])
        
        if get_action == 'stream':
            with lock:
                applyNumpyColors(strip, stream_data)

def time_thread(lock):
    global action, diff_time, initial_offset, start_time, ending_start_time, client, offset, stream_data
    c = ntplib.NTPClient()
    do_once = True
    while True:
        try:
            if client:
                response = c.request(client.getpeername()[0], version=4)
                if do_once:
                    initial_offset = response.offset
                    do_once = False
                with lock:
                    diff_time = response.dest_time + response.offset - time.time()
                    offset = response.offset
        except Exception as e:
            print(e)
        time.sleep(1)

def get_laptop_time():
    global action, diff_time, initial_offset, start_time, ending_start_time, client, offset
    return time.time() + offset
    #return time.time() + initial_offset - diff_time

def stream_thread(lock):
    global action, diff_time, initial_offset, start_time, ending_start_time, client, offset, stream_data
    server = socket.socket()
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('0.0.0.0', 9096))
    server.listen(1)
    stream_client, stream_client_address = server.accept()

    while True:
        data = stream_client.recv(4096)
        stream_client.send('next'.encode())
        with lock:
            stream_data = pickle.loads(data)

if __name__ == '__main__':
    global action, diff_time, initial_offset, start_time, ending_start_time, client, offset, stream_data
    lock = threading.Lock()
    barrier = threading.Barrier(2)

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
    colorWipe(strip)

    print('Loading video...')
    with open('/home/pi/ana-lights/mapping.json', 'r') as openfile:
        mapping = json.load(openfile)
    with open('/home/pi/ana-lights/position.json', 'r') as openfile:
        position = json.load(openfile)
    #video = np.load('/home/pi/ana-lights/lights/ana_lights_gbg.npy')
    video = np.load(mapping[position['position']])
    video_ending = np.load('/home/pi/ana-lights/lights/ana_ending.npy')
    fps = 30
    initial_offset = 0
    offset = 0

    client = None
    threading.Thread(target=time_thread, args=(lock,)).start()
    threading.Thread(target=lights_thread, args=(lock, barrier, strip, video, video_ending)).start()
    threading.Thread(target=stream_thread, args=(lock,)).start()

    while True:
        stripStatus(strip, [10,10,0])
        time.sleep(1)
        server = socket.socket()
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(('0.0.0.0', 9096))
        server.listen(1)
        stripStatus(strip, [10,0,0])
        print('Ready')
        client, client_address = server.accept()

        action = 'stop'

        while True:
            action_recv = client.recv(1024).decode()
            
            if action_recv == '':
                with lock:
                    action = 'stop'
                break
            if action_recv == 'start':
                client.send('RPi Zero ready to start'.encode())
                start_time_temp = float(client.recv(1024).decode())
                with lock:
                    start_time = start_time_temp
                    if action == 'stop' or action == 'pause' or action == 'ready':
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
                    if action == 'stop' or action == 'pause' or action == 'ready':
                        action = 'ending'
                        barrier.wait()
                    else:
                        action = 'ending'

            elif action_recv == 'mapping':
                with lock:
                    action = 'stop'
                select = client.recv(1024).decode()
                if select == 'map_select':
                    with lock:
                        action = 'map_select'
                        barrier.wait()
                    position = client.recv(1024).decode()
                    with open("/home/pi/ana-lights/position.json", "w") as outfile: 
                        outfile.write(json.dumps({'position': position})) 
                    with lock:
                        action = 'ready'

            elif action_recv == 'stream':
                with lock:
                    if action == 'stop' or action == 'pause' or action == 'ready':
                        action = 'stream'
                        barrier.wait()
                    else:
                        action = 'stream'