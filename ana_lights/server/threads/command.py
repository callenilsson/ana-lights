"""Thread listening for commands from the laptop."""
import time
import socket
import threading
import json
from . import global_vars
from ..led_strip import LEDStrip
from ...enums import Command, Port

# pylint: disable=global-statement, too-many-branches, too-many-statements


def get_command(lock: threading.Lock, laptop: socket.socket) -> Command:
    """"""
    try:
        command_recv = Command(laptop.recv(1024).decode("utf-8"))
    except ValueError as e:
        print(e, "HEJ2")
        with lock:
            global_vars.command = Command.STOP
        raise e
    return command_recv


def start(
    lock: threading.Lock,
    barrier: threading.Barrier,
    command_recv: Command,
    laptop: socket.socket,
) -> None:
    laptop.send(Command.READY.value.encode("utf-8"))
    start_time_temp = float(laptop.recv(1024).decode("utf-8"))
    if command_recv == Command.START:
        with lock:
            global_vars.start_time = start_time_temp
            if global_vars.command in (
                Command.STOP,
                Command.PAUSE,
                Command.READY,
            ):
                global_vars.command = Command.START
                barrier.wait()
            else:
                global_vars.command = Command.START


def stop_pause_resume(
    lock: threading.Lock,
    barrier: threading.Barrier,
    command_recv: Command,
) -> None:
    """"""
    if command_recv in (Command.STOP, Command.PAUSE):
        with lock:
            global_vars.command = command_recv

    if command_recv == Command.RESUME:
        with lock:
            global_vars.command = Command.START
            barrier.wait()


def map(
    lock: threading.Lock,
    barrier: threading.Barrier,
    command_recv: Command,
    laptop: socket.socket,
) -> None:
    """"""
    if command_recv == Command.MAP:
        with lock:
            global_vars.command = Command.STOP
        select = laptop.recv(1024).decode("utf-8")
        if select == Command.MAP_SELECT:
            with lock:
                global_vars.command = Command.MAP_SELECT
                barrier.wait()
            position = laptop.recv(1024).decode("utf-8")
            with open("mapping/pi_position.json", mode="w", encoding="utf-8") as f:
                f.write(json.dumps({"position": position}))
            with lock:
                global_vars.command = Command.READY


def stream(
    lock: threading.Lock,
    barrier: threading.Barrier,
    command_recv: Command,
) -> None:
    """"""
    if command_recv == Command.STREAM:
        with lock:
            if global_vars.command in (
                Command.STOP,
                Command.PAUSE,
                Command.READY,
            ):
                global_vars.command = Command.STREAM
                barrier.wait()
            else:
                global_vars.command = Command.STREAM


def command_thread(
    lock: threading.Lock,
    barrier: threading.Barrier,
    strip: LEDStrip,
) -> None:
    """Thread listening for commands from the laptop."""
    # Yellow status
    strip.status(red=10, green=10, blue=0)
    time.sleep(1)

    # Create server and wait for laptop to connect
    server_command = socket.socket()
    server_command.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_command.bind(("0.0.0.0", Port.COMMAND.value))  # nosec
    server_command.listen(1)

    # Green status
    strip.status(red=10, green=0, blue=0)
    print("Ready")
    laptop, _ = server_command.accept()

    # Update globals
    with lock:
        global_vars.laptop_ip = laptop.getpeername()[0]
        global_vars.command = Command.STOP

    while True:
        command_recv = get_command(lock, laptop)
        start(lock, barrier, command_recv, laptop)
        stop_pause_resume(lock, barrier, command_recv)
        map(lock, barrier, command_recv, laptop)
        stream(lock, barrier, command_recv)
