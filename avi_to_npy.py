import skvideo.io
import numpy as np
import pickle

def Color(red, green, blue, white=0):
    """Convert the provided red, green, blue color to a 24-bit color value.
    Each color component should be a value 0-255 where 0 is the lowest intensity
    and 255 is the highest intensity.
    """
    return (white << 24) | (red << 16) | (green << 8) | blue

video = skvideo.io.vread('videos/ana_lights_gbg6.avi')[:, :288, :1, :]
video = video.astype(np.uint8)
    
video_color = []
for i in range(len(video)):
    if i % 1000 == 0: print(i, '/', len(video))
    frame = video[i]
    frame_color = []
    for i in range(len(frame)):
        frame_color.append(Color(int(frame[i,0,1]), int(frame[i,0,0]), int(frame[i,0,2])))
    video_color.append(frame_color)

np.save('lights/ana_lights_gbg.npy', video_color)