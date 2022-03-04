"""Global variables."""
from ..enums import Command

# pylint: disable=global-statement

command: Command
x: int
y: int


def initialize() -> None:
    """Hej."""
    global command, x, y
    command = Command.STOP
    x = 0
    y = 0
