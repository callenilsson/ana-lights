"""Convert LED strips AVI video to JSON files."""
import json
import skvideo.io
from .color import Color

if __name__ == "__main__":
    video_name = "starlight"
    extension = "avi"
    video = skvideo.io.vread(f"videos/{video_name}.{extension}")[:, ::2, :, :]
    video = video[:, :144, :, :]

    # For each strip, write LED video pixel data to JSON file
    nbr_strips = 8
    for i in range(nbr_strips):

        # For each frame in video
        video_pixels = []
        for j, frame in enumerate(video):
            # Print progress
            if j % 1000 == 0:
                print(j, "/", len(video))

            # Get the x column of pixels in the video for the strip
            x = int(frame.shape[1] / (nbr_strips - 1) * i)
            if x == frame.shape[1]:
                x -= 1

            # Convert frame to list of pixels
            frame_pixels: list[int] = [
                Color(
                    red=int(frame[y, x, 1]),
                    green=int(frame[y, x, 0]),
                    blue=int(frame[y, x, 2]),
                )
                for y in range(len(frame))
            ]

            # Add frame pixels to the video
            video_pixels.append(frame_pixels)

        # Write LED video pixel data to JSON file
        with open(
            file=f"lights/{video_name}/strip_{i+1}.json", mode="w", encoding="utf-8"
        ) as f:
            json.dump(video_pixels, f)
