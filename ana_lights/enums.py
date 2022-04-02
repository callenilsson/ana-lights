"""Common enums."""
from enum import Enum

SONGS = [
    ["Cloudless skies", "00:00:00.00"],
    ["Pixeldye", "00:02:19.52"],
    ["Lumiére", "00:12:22.87"],
    ["Your name in the stars", "00:19:36.21"],
    ["Regn", "00:23:08.31"],
    ["You're somewhere", "00:27:23.13"],
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
