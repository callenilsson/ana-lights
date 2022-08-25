"""Common enums."""
from enum import Enum

SONGS = [
    ["Cloudless skies", "00:00:00.00"],
    ["Pixeldye", "00:04:15.827"],
    ["Lost yourself", "00:12:16.818"],
    ["Close to you", "00:17:18.082"],
    ["Lumiére", "00:21:47.593"],
    ["Regn", "00:26:23.286"],
    ["Starlight", "00:30:34.589"],
    ["You're somewhere", "00:35:30.639"],
]


class Command(Enum):
    """Available commands."""

    STREAM = "stream"
    RESUME = "resume"
    PAUSE = "pause"
    STOP = "stop"
    START = "start"
    MAP = "map"
    MAP_SELECT = "map_select"
    LOAD = "load"
    READY = "ready"
    NEXT = "next"


class Port(Enum):
    """Port numbers."""

    COMMAND = 9100
    STREAM = 9200


class LEDSettings:
    """Hej."""

    COUNT = 288  # Number of LED pixels.
    PIN = 13  # GPIO pin of the leds (18 uses PWM, 10 uses SPI /dev/spidev0.0)
    FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
    DMA = 10  # DMA channel to use for generating signal (try 10)
    BRIGHTNESS = 255  # Set to 0 for darkest and 255 for brightest
    INVERT = False  # True to invert signal (when using NPN transistor level shift)
    CHANNEL = 1  # set to '1' for GPIOs 13, 19, 41, 45 or 53
