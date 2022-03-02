"""Global variables."""
import socket
from ...enums import Command

command: Command
start_time: float
laptop_command: socket.socket
offset: float
pixels_stream: list[int]
