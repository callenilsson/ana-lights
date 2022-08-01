"""Convert LED strips AVI video to JSON files."""
import json
import skvideo.io
from .color import Color

if __name__ == "__main__":
    video = skvideo.io.vread("videos/test_render.mov")

    # For each strip, write LED video pixel data to JSON file
    nbr_strips = 10
    for i in range(nbr_strips):
        # For each frame in video
        video_pixels = []
        for j, frame in enumerate(video):
            # Get the x column of pixels in the video for the strip
            column_width = frame.shape[1] / nbr_strips
            x = int(column_width * (i + 1) - column_width / 2)

            # Print progress
            if j % 1000 == 0:
                print(f"{j}/{len(video)}, x={x}")

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
        with open(file=f"final_lights/strip_{i+1}.json", mode="w", encoding="utf-8") as f:
            json.dump(video_pixels, f)
