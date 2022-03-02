"""Stream pixels to all raspberry pies."""
import socket
import time
import json
from typing import List
import numpy as np
import mss
from ..color import Color


def stream_thread(pies_stream: List[socket.socket]) -> None:
    """Stream pixels to all raspberry pies."""
    # Read raspberry pi IP positions from JSON file
    with open("mapping/ip_positions.json", mode="r", encoding="utf-8") as f:
        ip_positions = json.load(f)

    # Initialize screen capture
    sct = mss.mss()
    mon = {"top": 400, "left": 930, "width": 1330, "height": 288}

    while True:
        # Start time of frame
        t = time.time()

        # Screen capture
        img = np.asarray(sct.grab(mon))[::-1, :, :3]  # *0.1
        img[:144, :, :] = img[::2, :, :]

        # Send pixels to all raspberry pies
        for pi in pies_stream:
            pixels = []
            for i in range(len(img)):
                # Get IP of the raspberry pi
                ip, _ = pi.getpeername()

                # Get the x column of pixels in the image for the strip
                x = int(mon["width"] / len(pies_stream) * (int(ip_positions[ip]) - 1))

                # Append pixel to pixels
                pixels.append(
                    Color(
                        red=int(img[i, x, 1]),
                        green=int(img[i, x, 2]),
                        blue=int(img[i, x, 0]),
                    )
                )

            # Send pixels to raspberry pi
            pi.send(json.dumps(pixels, ensure_ascii=False).encode("utf-8"))

        # Wait for ok to continue
        for pi in pies_stream:
            pi.recv(1024).decode("utf-8")

        # print(int(1/(time.time()-t)), 'fps')
