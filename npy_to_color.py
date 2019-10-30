import numpy as np
import pickle as p
from rpi_ws281x import *

video = np.load('lights/ana_ending.npy') 
video_color = []
for i in range(len(video[:10000])):
    if i % 100 == 0: print(i, '/', len(video))
    frame = video[i]
    frame_color = []
    for j in range(len(frame)):
        frame_color.append(Color(int(frame[j][0][1]), int(frame[j][0][0]), int(frame[j][0][2])))
    video_color.append(frame_color)
with open('lights/ana_ending_color.pkl', 'wb') as f:
    p.dump(video_color, f)