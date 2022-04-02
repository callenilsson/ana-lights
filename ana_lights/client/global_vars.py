"""Global variables."""
from ..enums import Command

# pylint: disable=global-statement

command: Command
x: int
y: int
stream_window: dict[str, int]


def initialize() -> None:
    """Hej."""
    global command, x, y, stream_window
    command = Command.STOP
    x = 0
    y = 0
    stream_window = {}
