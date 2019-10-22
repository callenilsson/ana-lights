import skvideo.io
import numpy as np

video = skvideo.io.vread('videos/ana_lights_gbg4.avi')[:, :288, :1, :]
video = video.astype(np.uint8)
print(video.shape)
np.save('lights/ana_lights_gbg.npy', video)
    
