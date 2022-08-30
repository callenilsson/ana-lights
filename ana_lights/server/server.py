"""Raspberry pi server."""
import threading
from .led_strip import LEDStrip
from .threads.time import time_thread
from .threads.lights import lights_thread
from .threads.command import command_thread
from .threads.stream import stream_thread
from .threads import global_vars
from ..enums import LEDSettings


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
    strip.status(red=0, green=0, blue=10)

    threading.Thread(target=time_thread, args=(lock,)).start()
    threading.Thread(target=lights_thread, args=(lock, barrier, strip)).start()

    while True:
        t1 = threading.Thread(target=stream_thread, args=(lock,))
        t2 = threading.Thread(target=command_thread, args=(lock, barrier, strip))
        t1.start()
        t2.start()
        t1.join()
        t2.join()
        print("Restarting stream and command thread")
