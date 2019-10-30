import skvideo.io
import numpy as np
import pickle

video = skvideo.io.vread('videos/ana_lights_gbg6.avi')[:, :288, :1, :]
video = video.astype(np.uint8)
print(video.shape)
np.save('lights/ana_lights_gbg.npy', video)
    
video_color = []
for frame in video:
    frame_color = []
    for i in range(len(frame)):
        frame_color.append(Color(int(frame[i][0][1]), int(frame[i][0][0]), int(frame[i][0][2])))
    video_color.append(frame_color)
with open('lights/ana_lights_gbg_color.obj', 'w') as f:
    pickle.dump(video_color, f)