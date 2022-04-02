"""Stream pixels to all raspberry pies."""
import json
import threading
import numpy as np
import mss
import cv2
from pynput import mouse
from . import global_vars
from .commands import RaspberryPI
from ..color import Color
from ..enums import Command, LEDSettings


def stream_thread(lock: threading.Lock, pies: list[RaspberryPI]) -> None:
    """Stream pixels to all raspberry pies."""
    # Read raspberry pi IP positions from JSON file
    with open("mapping/ip_positions.json", mode="r", encoding="utf-8") as f:
        ip_positions = json.load(f)

    # Initialize screen capture
    sct = mss.mss()

    # Read stream window size from JSON file
    with open("mapping/stream_window.json", mode="r", encoding="utf-8") as f:
        with lock:
            global_vars.stream_window = json.load(f)

    while True:
        with lock:
            if global_vars.command != Command.STREAM:
                break

        # Screen capture, and resize to height is same as number of leds
        with lock:
            img = np.asarray(sct.grab(global_vars.stream_window))[::-1, :, :3] * 0.1
        img = cv2.resize(
            img, dsize=(img.shape[1], LEDSettings.COUNT), interpolation=cv2.INTER_NEAREST
        )

        # Send pixels to all raspberry pies
        for pi in pies:
            pixels = []
            for i in range(len(img)):
                # Get the x column of pixels in the image for the strip
                with lock:
                    x = int(
                        global_vars.stream_window["width"]
                        / len(pies)
                        * (int(ip_positions[pi.ip]) - 1)
                    )

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

        # Wait for ok to continue
        for pi in pies:
            command = Command(pi.client.recv(1024).decode("utf-8"))
            if command != Command.NEXT:
                raise ValueError(
                    f"Raspberry PI sent '{command}' instead of '{Command.NEXT.value}'"
                )


def on_click(x: float, y: float, button: int, pressed: bool) -> bool:
    """Hej."""
    if button == mouse.Button.left:
        if pressed:
            print(f"Mouse pressed {int(x)}, {int(y)}")
            global_vars.x = int(x)
            global_vars.y = int(y)
            return False  # Return False to stop mouse listener.
    return True


def set_stream_window(lock: threading.Lock) -> None:
    """Hej."""
    print("---------------")
    window = {}
    # Mouse click 1
    with mouse.Listener(on_click=on_click) as listener:
        listener.join()
    x1 = global_vars.x
    y1 = global_vars.y

    # Mouse click 2
    with mouse.Listener(on_click=on_click) as listener:
        listener.join()
    x2 = global_vars.x
    y2 = global_vars.y

    # Add window to dict
    window["top"] = min(y2, y1)
    window["left"] = min(x2, x1)
    window["width"] = abs(x2 - x1)
    window["height"] = abs(y2 - y1)
    print("Updated stream window size to:", window)

    # Write window dict to JSON file
    with open("mapping/stream_window.json", mode="w", encoding="utf-8") as f:
        f.write(json.dumps(window))

    with lock:
        global_vars.stream_window = window
