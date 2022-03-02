"""Raspberry pi server."""
import threading
import json
from .led_strip import LEDStrip
from .threads.time import time_thread
from .threads.lights import lights_thread
from .threads.command import command_thread
from .threads import global_vars

# pylint: disable=global-statement, global-at-module-level

# LED strip configuration:
LED_COUNT = 144  # Number of LED pixels.
LED_PIN = 13  # GPIO pin connected to the pixels (18 uses PWM, 10 uses SPI /dev/spidev0.0)
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA = 10  # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255  # Set to 0 for darkest and 255 for brightest
LED_INVERT = False  # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL = 1  # set to '1' for GPIOs 13, 19, 41, 45 or 53


if __name__ == "__main__":
    global_vars.initialize()
    lock = threading.Lock()
    barrier = threading.Barrier(2)
    global_vars.offset = 0

    strip = LEDStrip(
        led_count=LED_COUNT,
        pin=LED_PIN,
        freq_hz=LED_FREQ_HZ,
        dma=LED_DMA,
        invert=LED_INVERT,
        brightness=LED_BRIGHTNESS,
        channel=LED_CHANNEL,
    )
    strip.black()

    print("Loading video...")
    with open("mapping/pi_position.json", mode="r", encoding="utf-8") as f:
        position = json.load(f)
    with open(f"lights/{position['position']}.json", mode="r", encoding="utf-8") as f:
        video = json.load(f)

    threading.Thread(target=time_thread, args=(lock,)).start()
    threading.Thread(target=lights_thread, args=(lock, barrier, strip, video)).start()
    command_thread(lock, barrier, strip)
