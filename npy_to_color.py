import numpy as np
import pickle as p

video = np.load('lights/ana_lights_gbg.npy') 
video_color = []
j = 0
for i in range(len(video)):
    if i % 100 == 0: print(i, '/', len(video))
    frame = video[i]
    frame_color = []
    for j in range(len(frame)):
        frame_color.append(Color(int(frame[j][0][1]), int(frame[j][0][0]), int(frame[j][0][2])))
    video_color.append(frame_color)
with open('lights/ana_lights_gbg_color.obj', 'w') as f:
    p.dump(video_color, f)