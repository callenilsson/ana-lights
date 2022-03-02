import skvideo.io
import time
from neopixel import *
import numpy as np
import math
from scipy import ndimage
import scipy.misc
import random
from multiprocessing import Process
import socket

def applyNumpyColors(strip, frame):
    for i in range(strip.numPixels()):
        #frame = np.clip(frame,0,230)
        strip.setPixelColor(i, Color(int(round(frame[i,1])), int(round(frame[i,0])), int(round(frame[i,2]))))
    strip.show()

def colorWipe(strip):
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, Color(0,0,0))
    strip.show()

def animate(strip, renders, start_time, interval):
    for i in range(len(renders)):
        current_time = time.time() - start_time
        goal_time = i/60.0
        if goal_time < current_time:
            continue
            
        start_iter_time = time.time()
        applyNumpyColors(strip, renders[i])
        
        wait = 1/60.0 - (time.time() - start_iter_time)
        if wait > 0:
            time.sleep(wait)
        


        
if __name__ == '__main__':
    # LED strip configuration:
    LED_COUNT      = 144    # Number of LED pixels.
    LED_PIN        = 12      # GPIO pin connected to the pixels (18 uses PWM!).
    #LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
    LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
    LED_DMA        = 10      # DMA channel to use for generating signal (try 10)
    LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
    LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
    LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53

    strip1 = Adafruit_NeoPixel(144, 12, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, 0)
    strip2 = Adafruit_NeoPixel(288, 13, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, 1)
    strip3 = Adafruit_NeoPixel(288, 19, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, 1)
    strip1.begin()
    strip2.begin()
    strip3.begin()
    fps = 60.0

    # Read video to numpy array
    renders = np.zeros((22000,300,3))
    videogen = skvideo.io.vreader('cloudless_lights_3.avi')
    i = 0
    for frame in videogen:
        print(i)
        renders[i] = frame[:,0,:]
        i += 1

    #renders = cv2.resize(img, dsize(10000,288,3), interpolation=cv2.INTER_NEAREST)

    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        server.bind(("", 44444))
        raw_input('Press Enter to start')
        print('Starting animations...')
        start_time = time.time()
        server.sendto(b"start_animations_now" + str(start_time), ('<broadcast>', 37020))
        p1 = Process(target=animate, args=(strip1, renders, start_time, [0,8000]))
        p2 = Process(target=animate, args=(strip2, renders, start_time, [0,8000]))
        #p3 = Process(target=animate, args=(strip3, renders, start_time, [0,8000]))
        p1.start()
        p2.start()
        #p3.start()
        p1.join()
        p2.join()
        #p3.join()

    except:
        colorWipe(strip1)
        colorWipe(strip2)
        #colorWipe(strip3)
