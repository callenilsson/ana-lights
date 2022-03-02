"""Common enums."""
from enum import Enum

SONGS = [
    ["Cloudless skies", "00:00:03:69"],
    ["Pixeldye", "00:04:19.52"],
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
