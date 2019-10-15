import time
from neopixel import *
import numpy as np
import math
from scipy import ndimage
import scipy.misc
import random
#import cv2

def tick(np_strip, bpm, res, bar_length, direction, mirror):
    global remainder, fps

    time_per_beat = 3*60.0/bpm
    updates_per_beat = time_per_beat / (1.0/fps)
    skip = bar_length / updates_per_beat + remainder
    remainder = skip - int(skip)
    skip = int(skip)

    if skip == 0:
        print('Increase resolution')
    else:
        if direction == -1:
            temp = np.copy(np_strip[:skip, :])
            np_strip[:-skip, :] = np_strip[skip:, :]
            if mirror:
                np_strip[-skip:, :] = temp
            else:
                np_strip[-skip:, :] = np.zeros((skip, 3))
        else:
            temp = np.copy(np_strip[-skip:, :])
            np_strip[skip:, :] = np_strip[:-skip, :]
            if mirror:
                np_strip[:skip, :] = temp
            else:
                np_strip[:skip, :] = np.zeros((skip, 3))
    return np_strip

def colorWipe():
    global strip, LED_COUNT, start_time
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, Color(0,0,0))
    strip.show()

def applyNumpyColors(strip, frame):
    for i in range(strip.numPixels()):
        frame = np.clip(frame,0,255)
        strip.setPixelColor(i, Color(int(round(frame[i,1])), int(round(frame[i,0])), int(round(frame[i,2]))))
    strip.show()

def screen_blend(a, b):
    ones = np.ones(a.shape)
    return 255*(ones - (ones - a/255)*(ones - b/255))


def constant_color(duration, fadein, fadeout, color):
    global LED_COUNT, renders, remainder, fps

    # Add each frame to renders
    i = int(duration[0]*fps)
    last_percentage = -1
    while i < int(duration[1]*fps):
        if not(int(100*i/int(duration[1]*fps)) == last_percentage):
            last_percentage = int(100*(i - int(duration[0]*fps))/(int(duration[1]*fps) - int(duration[0]*fps)))
            print(str(duration[0]) + ' - ' + str(duration[1]) + '\tConstant color:\t' + str(last_percentage) + '%')

        short_strip = np.ones((LED_COUNT, 3))*color

        # Fade in
        if i - int(duration[0]*fps) < fadein*fps:
            j = i - int(duration[0]*fps)
            fade_percentage = j / (fadein*fps)
            short_strip = short_strip*fade_percentage
        # Fade out
        if i - int(duration[0]*fps) > int(duration[1]*fps) - int(duration[0]*fps) - fadeout*fps:
            j = i - int(duration[0]*fps) - (int(duration[1]*fps) - int(duration[0]*fps) - int(fadeout*fps))
            fade_percentage = 1 - j / (fadeout*fps)
            short_strip = short_strip*fade_percentage

        # If overlap with previous render, screen blend. Else add new frame
        renders[i] = screen_blend(renders[i], short_strip)
        i += 1

def noise(duration, fadein, fadeout, intensity):
    global LED_COUNT, renders, remainder, fps

    # Apply noise to selected frames
    i = int(duration[0]*fps)
    while i < int(duration[1]*fps):
        x = random.random()
        noise = np.clip(math.exp(-10*x) - 0.2*x + 0.2, 0, 1)*intensity

        # Fade in
        if i - int(duration[0]*fps) < fadein*fps:
            j = i - int(duration[0]*fps)
            fade_percentage = j / (fadein*fps)
            noise = noise*fade_percentage
        # Fade out
        if i - int(duration[0]*fps) > int(duration[1]*fps) - int(duration[0]*fps) - fadeout*fps:
            j = i - int(duration[0]*fps) - (int(duration[1]*fps) - int(duration[0]*fps) - int(fadeout*fps))
            fade_percentage = 1 - j / (fadeout*fps)
            noise = noise*fade_percentage

        renders[i] = renders[i]*(1-noise)
        i += 1


def strobe(duration, fadein, fadeout, bpm, intensity_interval):
    global LED_COUNT, renders, remainder, fps

    # Add each frame to renders
    i = int(duration[0]*fps)
    last_div = -1
    strobe = intensity_interval[0]
    while i < int(duration[1]*fps):
        time_per_beat = 60.0/bpm
        skip = time_per_beat / (1.0/fps)

        if int((i-duration[0]*fps) / skip) > last_div:
            last_div = int((i-duration[0]*fps) / skip)
            if strobe == intensity_interval[0]: strobe = intensity_interval[1]
            else:                               strobe = intensity_interval[0]

        # Fade in
        if i - int(duration[0]*fps) < fadein*fps:
            j = i - int(duration[0]*fps)
            fade_percentage = j / (fadein*fps)
            strobe = strobe*fade_percentage
        # Fade out
        if i - int(duration[0]*fps) > int(duration[1]*fps) - int(duration[0]*fps) - fadeout*fps:
            j = i - int(duration[0]*fps) - (int(duration[1]*fps) - int(duration[0]*fps) - int(fadeout*fps))
            fade_percentage = 1 - j / (fadeout*fps)
            strobe = strobe*fade_percentage

        renders[i] = renders[i]*strobe
        i += 1


def multiple_colors(duration, fadein, fadeout, bpm, filter_length, res, direction, color_list):
    global LED_COUNT, renders, remainder, fps

    start_time = time.time()
    # Construct np_strip, with evenly distributed colors
    length = math.ceil(LED_COUNT/filter_length)*filter_length + 2*filter_length
    while not((length/filter_length + 1) % len(color_list) == 1):
        length += filter_length
    long_strip = np.zeros((int(length*res), 3))
    for i in range(int(len(long_strip)/(filter_length*res)) + 1):
        if i == 0: idx = 0
        else: idx = i*filter_length*res - 1
        long_strip[idx] = color_list[i%len(color_list)]

    # Construct convolution filter
    filter = np.linspace(0, 1, num=filter_length*res)
    filter = np.append(filter[:-1], filter[::-1])

    # Convolution
    long_strip = np.append(np.convolve(long_strip[:, 0], filter, 'same'),
                            [np.convolve(long_strip[:, 1], filter, 'same'),
                            np.convolve(long_strip[:, 2], filter, 'same')]).reshape(len(long_strip), 3, order='F')
    long_strip = long_strip[:-1]

    # Skip to correct time
    for i in range(int((duration[0]*fps) % (60.0/bpm*3*fps*len(color_list)))):
        long_strip = tick(long_strip, bpm, res, filter_length*res, direction, mirror=True)

    # Add each frame to renders
    i = int(duration[0]*fps)
    last_percentage = -1

    while i < int(duration[1]*fps):
        if not(int(100*i/int(duration[1]*fps)) == last_percentage):
            last_percentage = int(100*(i - int(duration[0]*fps))/(int(duration[1]*fps) - int(duration[0]*fps)))
            print(str(duration[0]) + ' - ' + str(duration[1]) + '\tMultiple colors:\t' + str(last_percentage) + '%')

        long_strip = tick(long_strip, bpm, res, filter_length*res, direction, mirror=True)

        #short_strip = skimage.transform.resize(long_strip, [LED_COUNT,3])
        #print(short_strip.shape)

        short_strip = long_strip[::res]
        short_strip = short_strip[:LED_COUNT]

        # Fade in
        if i - int(duration[0]*fps) < fadein*fps:
            j = i - int(duration[0]*fps)
            fade_percentage = j / (fadein*fps)
            short_strip = short_strip*fade_percentage
        # Fade out
        if i - int(duration[0]*fps) > int(duration[1]*fps) - int(duration[0]*fps) - fadeout*fps:
            j = i - int(duration[0]*fps) - (int(duration[1]*fps) - int(duration[0]*fps) - int(fadeout*fps))
            fade_percentage = 1 - j / (fadeout*fps)
            short_strip = short_strip*fade_percentage

        renders[i] = screen_blend(renders[i], short_strip)
        i += 1



def particles(duration, bpm, tail_length, birth_rate, birth_random, res, direction, color_list):
    global LED_COUNT, renders, remainder, fps

    # Initialize first particle
    master_particles = np.zeros((LED_COUNT*res + tail_length*res,3))
    if direction == 1:
        master_particles[0,0] = 1
    else:
        master_particles[-1,0] = 1

    # Render each frame
    spawn_new_particle = int(duration[0]*fps)+1
    i = int(duration[0]*fps)
    last_percentage = -1
    while i < int(duration[1]*fps) or not(np.sum(master_particles) == 0):
        if not(int(100*i/int(duration[1]*fps)) == last_percentage):
            last_percentage = int(100*(i - int(duration[0]*fps))/(int(duration[1]*fps) - int(duration[0]*fps)))
            print(str(duration[0]) + ' - ' + str(duration[1]) + '\tParticles:\t' + str(last_percentage) + '%')

        # Spawn another particle?
        if i % spawn_new_particle == 0 and i < int(duration[1]*fps):
            spawn_new_particle += random.randint(fps/birth_rate-(fps/birth_rate)*birth_random, fps/birth_rate+(fps/birth_rate)*birth_random)
            if direction == 1:
                master_particles[0,0] = 1
            else:
                master_particles[-1,0] = 1

        # Construct master particles and tail particles
        master_particles = tick(master_particles, bpm, res, LED_COUNT*res, direction, mirror=False)
        tail_particles = np.zeros((LED_COUNT*res + tail_length*res,3))
        for j in np.argwhere(master_particles > 0):
            j = j[0]
            temp_tail_particles = np.zeros((LED_COUNT*res + tail_length*res,3))

            actual_tail = 0
            if direction == 1:
                if j - tail_length*res < 0: actual_tail = j
                else: actual_tail = tail_length*res
            else:
                if j + tail_length*res > len(tail_particles): actual_tail = len(tail_particles) - j
                else: actual_tail = tail_length*res

            alpha = np.linspace(0, master_particles[j,0], actual_tail).reshape(actual_tail,1)
            alpha_inv = np.linspace(master_particles[j,0], 0, actual_tail).reshape(actual_tail,1)

            if direction == 1:
                temp_tail_particles[j-actual_tail:j, :] = alpha*(alpha*np.ones((actual_tail,1))*color_list[0] + alpha_inv*np.ones((actual_tail,1))*color_list[1])
            else:
                temp_tail_particles[j:j+actual_tail, :] = alpha_inv*(alpha_inv*np.ones((actual_tail,1))*color_list[0] + alpha*np.ones((actual_tail,1))*color_list[1])
            tail_particles = screen_blend(tail_particles, temp_tail_particles)

        # Normalize values above 255
        tail_particles = np.clip(tail_particles,0,255)
        #tail_particles = np.resize(tail_particles, (LED_COUNT,3))
        tail_particles = tail_particles[::res]
        if direction == 1:
            tail_particles = tail_particles[:LED_COUNT]
        else:
            tail_particles = tail_particles[tail_length:LED_COUNT+tail_length]

        renders[i] = screen_blend(renders[i], tail_particles)
        i += 1

def ElasticEaseInOut(p):
    if (p < 0.5):
        return 0.5 * math.sin(9 * math.pi*math.pi * (2 * p)) * math.pow(2, 5 * ((2 * p) - 1))
    else:
        return 0.5 * (math.sin(-9 * math.pi*math.pi * ((2 * p - 1) + 1)) * math.pow(2, -5 * (2 * p - 1)) + 2)


def march(duration, fadein, fadeout, bpm, res, length_interval, opacity_interval):
    global LED_COUNT, renders, remainder, fps

    # Add each frame to renders
    i = int(duration[0]*fps)
    last_percentage = -1
    on = True
    last_div = -1
    on = False
    while i < int(duration[1]*fps):
        if not(int(100*i/int(duration[1]*fps)) == last_percentage):
            last_percentage = int(100*(i - int(duration[0]*fps))/(int(duration[1]*fps) - int(duration[0]*fps)))
            print(str(duration[0]) + ' - ' + str(duration[1]) + '\tMarch:\t' + str(last_percentage) + '%')

        time_per_beat = 60.0/bpm
        skip = time_per_beat / (1.0/fps)

        t = ((i/fps - duration[0]) % time_per_beat)/time_per_beat

        #v = easeInOut(t, 0.0, 1.0, time_per_beat)
        v = ElasticEaseInOut(t)

        if int((i-duration[0]*fps) / skip) > last_div:
            last_div = int((i-duration[0]*fps) / skip)
            on = not(on)
        if on:
            v = 1.0 - v
        v += 0.05
        v = int(round(LED_COUNT*res* (v*(length_interval[1] - length_interval[0]) + length_interval[0])))



        long_strip = np.ones((LED_COUNT*res, 3))*opacity_interval[1]
        long_strip[v:] = [opacity_interval[0], opacity_interval[0], opacity_interval[0]]

        short_strip = long_strip[::res]
        short_strip = short_strip[:LED_COUNT]

        # Fade in
        if i - int(duration[0]*fps) < fadein*fps:
            j = i - int(duration[0]*fps)
            fade_percentage = j / (fadein*fps)
            short_strip = short_strip*fade_percentage
        # Fade out
        if i - int(duration[0]*fps) > int(duration[1]*fps) - int(duration[0]*fps) - fadeout*fps:
            j = i - int(duration[0]*fps) - (int(duration[1]*fps) - int(duration[0]*fps) - int(fadeout*fps))
            fade_percentage = 1 - j / (fadeout*fps)
            short_strip = short_strip*fade_percentage

        renders[i] = renders[i]*short_strip
        i += 1



def animate(strip, renders, x, interval):
    remainder_time = 0
    start_time = time.time()

    i = int(interval[0]*fps)
    if len(renders) < int(interval[1]*fps):
        end = len(renders)
    else:
        end = int(interval[1]*fps)
    while i < end:
        iter_time = time.time()

        applyNumpyColors(strip, renders[i]/x)

        error = time.time() + interval[0] - start_time - i/60.0
        #print('Actual time: ' + str(time.time() + interval[0] - start_time) + '\tError: ' + str(error))

        # Calculate time to wait until next iteration
        wait = 1.0/fps - (time.time() - iter_time) - error
        remainder_time = 0
        if wait > 0:
            time.sleep(wait)

        i += 1

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
    fps = 60.0
    renders = np.zeros((int(1000*fps), LED_COUNT, 3))
    remainder = 0

    try:
        print('Rendering animations...')
        x = 25
        bt3 = 3*60.0/124
        bt4 = 4*60.0/124

        # Effect Demo
        #constant_color(duration=[0.0,4.0], fadein=0, fadeout=0, color=[0,0,5])
        #constant_color(duration=[4.0,8.0], fadein=0, fadeout=0, color=[0,0,5])
        #multiple_colors(duration=[12.0,16.5], fadein=0, fadeout=1, bpm=120*4, filter_length=20, res=30, direction=1, color_list=[[0,0,5], [5,0,0]])
        #noise(duration=[4.0,8.0], fadein=0, fadeout=0, intensity=0.8)
        #constant_color(duration=[8.0,12.0], fadein=0, fadeout=0, color=[5,5,5])
        #strobe(duration=[8.0,12.0], fadein=0, fadeout=0, bpm=120*16, intensity_interval=[0.0, 1.0])
        #multiple_colors(duration=[12.0,16.5], fadein=0, fadeout=1, bpm=120*4, filter_length=20, res=30, direction=1, color_list=[[0,0,5], [5,0,0]])
        #multiple_colors(duration=[15.5,20.0], fadein=1, fadeout=0, bpm=120*4, filter_length=20, res=30, direction=1, color_list=[[0,0,5], [0,5,0]])
        #multiple_colors(duration=[20.0,24.0], fadein=0, fadeout=0, bpm=120*4, filter_length=20, res=30, direction=1, color_list=[[0,5,5], [0,0,5]])
        #march(duration=[20.0, 24.0], fadein=0, fadeout=0, bpm=120*2, res=10, length_interval=[0.2, 0.5], opacity_interval=[0.2, 1.0])
        #particles(duration=[24.0,32.0], bpm=120, tail_length=20, birth_rate=4, birth_random=0.8, res=10, direction=1, color_list=[[0,0,5], [0,5,5]])
        #particles(duration=[28.0,32.0], bpm=120, tail_length=20, birth_rate=4, birth_random=0.8, res=10, direction=-1, color_list=[[5,0,0], [5,5,0]])

        # Any Given Place Test
        #multiple_colors(duration=[bt*0, bt*8], fadein=0, fadeout=0, bpm=141, filter_length=20, res=50, direction=1, color_list=[[0,0,5], [0,0,0]])
        #multiple_colors(duration=[bt*4, bt*8], fadein=12.2, fadeout=0, bpm=141*16, filter_length=20, res=30, direction=1, color_list=[[10,10,10], [0,0,0]])
        #multiple_colors(duration=[bt*9, bt*13+0.3], fadein=0, fadeout=0.6, bpm=141*4, filter_length=100, res=30, direction=1, color_list=[[10,9,6], [5,3,1]])
        #multiple_colors(duration=[bt*13-0.3, bt*17], fadein=0.6, fadeout=0, bpm=141*4, filter_length=100, res=30, direction=1, color_list=[[10,6,9], [5,1,4]])
        #multiple_colors(duration=[bt*17, bt*25], fadein=0, fadeout=0.0, bpm=141*4, filter_length=100, res=30, direction=1, color_list=[[10,10,10], [4,4,4]])
        #strobe(duration=[bt*17,bt*25], fadein=0, fadeout=0, bpm=141*16, intensity_interval=[0.3, 1.0])

        # Pixeldye
        particles(duration=[bt3*0, bt3*24], bpm=124, tail_length=30, birth_rate=2, birth_random=0, res=10, direction=1, color_list=[[200,200,200], [0,110,200]])
        multiple_colors(duration=[bt3*24-0.2, bt3*32+0.5], fadein=0.4, fadeout=1, bpm=124, filter_length=100, res=10, direction=1, color_list=[[200,0,0], [40,0,0]])
        multiple_colors(duration=[bt3*32-0.5, bt3*72+1], fadein=1, fadeout=0, bpm=124/2, filter_length=100, res=10, direction=1, color_list=[[0,80,120], [0,0,30]])
        multiple_colors(duration=[bt3*52, bt3*72+2], fadein=bt3*20, fadeout=2, bpm=124*9, filter_length=50, res=10, direction=1, color_list=[[190,220,255], [0,0,0]])
        constant_color(duration=[bt3*72, bt3*81], fadein=0, fadeout=0, color=[1,5,10])
        noise(duration=[bt3*72, bt3*81], fadein=0, fadeout=0, intensity=0.8)
        constant_color(duration=[bt3*81, bt3*82], fadein=0, fadeout=1.4, color=[255,190,130])

        multiple_colors(duration=[bt3*82, bt3*86+0.1], fadein=0, fadeout=0.2, bpm=124*6, filter_length=200, res=10, direction=1, color_list=[[255,30,30], [120,10,10]])
        multiple_colors(duration=[bt3*86-0.1, bt3*90+0.1], fadein=0.2, fadeout=0.2, bpm=124*6, filter_length=200, res=10, direction=1, color_list=[[170,100,255], [50,0,125]])
        multiple_colors(duration=[bt3*90-0.1, bt3*94+0.1], fadein=0.2, fadeout=0.2, bpm=124*6, filter_length=200, res=10, direction=1, color_list=[[220,100,255], [100,0,125]])
        multiple_colors(duration=[bt3*94-0.1, bt3*96+0.1], fadein=0.2, fadeout=0.2, bpm=124*6, filter_length=200, res=10, direction=1, color_list=[[255,100,220], [125,0,100]])
        multiple_colors(duration=[bt3*96-0.1, bt3*97+0.1], fadein=0.2, fadeout=0.2, bpm=124*6, filter_length=200, res=10, direction=1, color_list=[[255,100,160], [125,0,60]])
        multiple_colors(duration=[bt3*97-0.1, bt3*98], fadein=0.2, fadeout=0, bpm=124*6, filter_length=200, res=10, direction=1, color_list=[[255,140,170], [125,55,85]])
        constant_color(duration=[bt3*98,bt3*106], fadein=0, fadeout=0, color=[160,220,255])
        strobe(duration=[bt3*98,bt3*106], fadein=0, fadeout=0, bpm=124*12, intensity_interval=[0.0, 1.0])

        multiple_colors(duration=[bt3*106, bt3*108+0.1], fadein=0, fadeout=0.2, bpm=124*6, filter_length=200, res=10, direction=1, color_list=[[170,100,255], [50,0,125]])
        multiple_colors(duration=[bt3*108-0.1, bt3*109+0.1], fadein=0.2, fadeout=0.2, bpm=124*6, filter_length=200, res=10, direction=1, color_list=[[255,100,220], [125,0,100]])
        multiple_colors(duration=[bt3*109-0.1, bt3*110+0.1], fadein=0.2, fadeout=0.2, bpm=124*6, filter_length=200, res=10, direction=1, color_list=[[255,140,160], [125,55,85]])
        multiple_colors(duration=[bt3*110-0.1, bt3*114+0.1], fadein=0.2, fadeout=0.2, bpm=124*6, filter_length=200, res=10, direction=1, color_list=[[170,100,255], [50,0,125]])
        multiple_colors(duration=[bt3*114-0.1, bt3*117+0.1], fadein=0.2, fadeout=0.2, bpm=124*6, filter_length=200, res=10, direction=1, color_list=[[255,100,220], [125,0,100]])
        multiple_colors(duration=[bt3*117-0.1, bt3*118+0.1], fadein=0.2, fadeout=0.2, bpm=124*6, filter_length=200, res=10, direction=1, color_list=[[255,140,160], [125,55,85]])
        multiple_colors(duration=[bt3*118-0.1, bt3*120], fadein=0.2, fadeout=0, bpm=124*6, filter_length=200, res=10, direction=1, color_list=[[170,100,255], [50,0,125]])
        strobe(duration=[bt3*106,bt3*120], fadein=0, fadeout=0, bpm=124*12, intensity_interval=[0.2, 1.0])
        constant_color(duration=[bt3*120, bt3*120+4], fadein=0, fadeout=4, color=[200,100,255])

        multiple_colors(duration=[bt3*124, bt3*186], fadein=bt3*4, fadeout=0, bpm=124/2, filter_length=100, res=10, direction=1, color_list=[[0,80,120], [0,0,30]])
        multiple_colors(duration=[bt3*156, bt3*186], fadein=bt3*30, fadeout=0, bpm=124*4, filter_length=50, res=10, direction=1, color_list=[[40,100,120], [5,15,30]])

        multiple_colors(duration=[bt3*186, bt3*194], fadein=0, fadeout=0, bpm=124, filter_length=100, res=10, direction=1, color_list=[[200,0,0], [40,0,0]])
        multiple_colors(duration=[bt3*194, bt3*195], fadein=0, fadeout=0, bpm=124, filter_length=100, res=10, direction=1, color_list=[[0,200,0], [0,40,0]])
        multiple_colors(duration=[bt3*195, bt3*195+bt4], fadein=0, fadeout=0, bpm=124, filter_length=100, res=10, direction=1, color_list=[[200,200,0], [40,40,0]])
        multiple_colors(duration=[bt3*195+bt4, bt4+bt3*201], fadein=0, fadeout=0, bpm=124, filter_length=100, res=10, direction=1, color_list=[[200,0,0], [40,0,0]])
        multiple_colors(duration=[bt3*201+bt4, bt4+bt3*202], fadein=0, fadeout=0, bpm=124, filter_length=100, res=10, direction=1, color_list=[[200,200,0], [40,40,0]])
        multiple_colors(duration=[bt4+bt3*202, bt4+bt3*230+1], fadein=0, fadeout=0, bpm=124/2, filter_length=100, res=10, direction=1, color_list=[[0,40,120], [0,20,50]])


        raw_input("Press Enter to start...")

        print('Starting animations...')
        animate(strip, renders, x, interval=[bt3*0,bt3*300])

    except KeyboardInterrupt:
        colorWipe()
