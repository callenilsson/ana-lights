"""Convert LED strips AVI video to JSON files."""
import json
import glob
import imageio
from .color import Color

if __name__ == "__main__":
    # For each strip, write LED video pixel data to JSON file
    frame_paths = sorted(list(glob.glob("videos/test_render/*.png")))

    nbr_strips = 10
    strips: list[list[list[int]]] = [[] for _ in range(nbr_strips)]
    for frame_nbr, img_path in enumerate(frame_paths):
        frame = imageio.imread(img_path)

        # Print progress
        if frame_nbr % 1000 == 0 and frame_nbr > 0:
            print(f"{frame_nbr}/{len(frame_paths)}")

        for strip_nbr in range(nbr_strips):
            # Get the x column of pixels in the video for the strip
            column_width = frame.shape[1] / nbr_strips
            x = int(column_width * (strip_nbr + 1) - column_width / 2)

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
            strips[strip_nbr].append(frame_pixels)

    # Write LED video pixel data to JSON file
    for strip_nbr, strip in enumerate(strips):
        with open(
            file=f"final_lights/strip_{strip_nbr+1}.json", mode="w", encoding="utf-8"
        ) as f:
            json.dump(strip, f)
