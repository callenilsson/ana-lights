import skvideo.io
import numpy as np

video = skvideo.io.vread('videos/ana_lights_gbg6.avi')[:10000, :288, :1, :]
video = video.astype(np.uint8)
print(video.shape)
np.save('lights/ana_lights_gbg_lite.npy', video)
    
