import skvideo.io
import numpy as np
import pickle

def Color(red, green, blue, white=0):
    """Convert the provided red, green, blue color to a 24-bit color value.
    Each color component should be a value 0-255 where 0 is the lowest intensity
    and 255 is the highest intensity.
    """
    return (white << 24) | (red << 16) | (green << 8) | blue

video_name = 'starlight.avi'
video = skvideo.io.vread('videos/' + video_name)[:, ::2, :, :]
video = video[:, :144, :, :]
video = video.astype(np.uint8)
    

nbr_strips = 8
for i in range(nbr_strips):
    video_color = []
    for j in range(len(video)):
        if j % 1000 == 0: print(j, '/', len(video))
        frame = video[j]
        frame_color = []
        x = int(len(frame[:,0])/nbr_strips * i)
        for k in range(len(frame)):
            frame_color.append(Color(int(frame[k,x,1]), int(frame[k,x,0]), int(frame[k,x,2])))
        video_color.append(frame_color)

    np.save('lights/' + video_name[:-4] + '_' + str(i+1) + '.npy', video_color)