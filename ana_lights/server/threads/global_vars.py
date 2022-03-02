"""Global variables."""
import socket
from typing import List
from ...enums import Command


def initialize():
    global command, start_time, laptop_command, offset, pixels_stream
    command: Command
    start_time: float
    laptop_command: socket.socket
    offset: float
    pixels_stream: List[int]
