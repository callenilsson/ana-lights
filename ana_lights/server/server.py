"""Raspberry pi server."""
import threading
import json
from .led_strip import LEDStrip
from .threads.time import time_thread
from .threads.lights import lights_thread
from .threads.command import command_thread
from .threads.stream import stream_thread
from .threads import global_vars
from ..enums import LEDSettings

# pylint: disable=global-statement, global-at-module-level


if __name__ == "__main__":
    global_vars.initialize()
    lock = threading.Lock()
    barrier = threading.Barrier(2)
    global_vars.offset = 0

    strip = LEDStrip(
        led_count=LEDSettings.COUNT,
        pin=LEDSettings.PIN,
        freq_hz=LEDSettings.FREQ_HZ,
        dma=LEDSettings.DMA,
        invert=LEDSettings.INVERT,
        brightness=LEDSettings.BRIGHTNESS,
        channel=LEDSettings.CHANNEL,
    )
    strip.black()

    print("Loading video...")
    with open("mapping/pi_position.json", mode="r", encoding="utf-8") as f:
        position = json.load(f)
    with open(
        f"final_lights/strip_{position['position']}_30fps.json",
        mode="r",
        encoding="utf-8",
    ) as f:
        video = json.load(f)

    threading.Thread(target=time_thread, args=(lock,)).start()
    threading.Thread(target=lights_thread, args=(lock, barrier, strip, video)).start()

    while True:
        t1 = threading.Thread(target=stream_thread, args=(lock,))
        t2 = threading.Thread(target=command_thread, args=(lock, barrier, strip))
        t1.start()
        t2.start()
        t1.join()
        t2.join()
        print("Restarting stream and command thread")
