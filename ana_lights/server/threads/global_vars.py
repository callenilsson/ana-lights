"""Global variables."""
from ...enums import Command, LEDSettings

# pylint: disable=global-statement

command: Command
song_start: float
start_time: float
laptop_ip: str
offset: float
pixels_stream: list[int]
fps: int


def initialize() -> None:
    """Hej."""
    global command, song_start, start_time, laptop_ip, offset, pixels_stream, fps
    command = Command.STOP
    song_start = 0.0
    start_time = 0.0
    laptop_ip = ""
    offset = 0.0
    pixels_stream = [0] * LEDSettings.COUNT
    fps = 0
