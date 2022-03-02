"""Stream pixels to all raspberry pies."""
from glob import glob
import time
import json
import threading
from typing import List
import numpy as np
import mss
from .raspberry_pies import RaspberryPI
from ..color import Color
from ..enums import Command
from . import global_vars


def stream_thread(lock: threading.Lock, pies: List[RaspberryPI]) -> None:
    """Stream pixels to all raspberry pies."""
    # Read raspberry pi IP positions from JSON file
    with open("mapping/ip_positions.json", mode="r", encoding="utf-8") as f:
        ip_positions = json.load(f)

    # Initialize screen capture
    sct = mss.mss()
    scale = 2
    mon = {"top": 400, "left": 930, "width": 1330, "height": 288}

    while True:
        with lock:
            if global_vars.command == Command.STOP:
                break

        # Start time of frame
        t = time.time()

        # Screen capture
        img = (
            np.asarray(sct.grab({k: int(v / scale) for k, v in mon.items()}))[::-1, :, :3]
            * 0.1
        )
        t2 = time.time()

        # Send pixels to all raspberry pies
        for pi in pies:
            pixels = []
            for i in range(len(img)):
                # Get the x column of pixels in the image for the strip
                x = int(mon["width"] / len(pies) * (int(ip_positions[pi.ip]) - 1))

                # Append pixel to pixels
                pixels.append(
                    Color(
                        red=int(img[i, x, 1]),
                        green=int(img[i, x, 2]),
                        blue=int(img[i, x, 0]),
                    )
                )

            # Send pixels to raspberry pi
            pi.client.send(json.dumps(pixels, ensure_ascii=False).encode("utf-8"))

        t3 = time.time()

        # Wait for ok to continue
        for pi in pies:
            command = Command(pi.client.recv(1024).decode("utf-8"))
            if command != Command.NEXT:
                raise ValueError(
                    f"Raspberry PI sent '{command}' instead of '{Command.NEXT.value}'"
                )

        t4 = time.time()
        if int(1 / (time.time() - t)) < 20:
            print((t2 - t) * 1000)
            print((t3 - t2) * 1000)
            print((t4 - t3) * 1000)
            print(int(1 / (time.time() - t)), "fps")
            print()
