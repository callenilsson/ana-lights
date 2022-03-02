"""Thread listening for commands from the laptop."""
import time
import socket
import threading
import json
from . import global_vars
from .stream import stream_thread
from ..led_strip import LEDStrip
from ...enums import Command, Port

# pylint: disable=global-statement, too-many-branches, too-many-statements


def command_thread(
    lock: threading.Lock,
    barrier: threading.Barrier,
    strip: LEDStrip,
) -> None:
    """Thread listening for commands from the laptop."""
    while True:
        strip.status(red=10, green=10, blue=0)
        time.sleep(1)
        threading.Thread(target=stream_thread, args=(lock,)).start()
        server_command = socket.socket()
        server_command.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_command.bind(("0.0.0.0", Port.COMMAND.value))  # nosec
        server_command.listen(1)
        strip.status(red=10, green=0, blue=0)
        print("Ready")
        global_vars.laptop_command, _ = server_command.accept()

        global_vars.command = Command.STOP

        while True:
            try:
                command_recv = Command(
                    global_vars.laptop_command.recv(1024).decode("utf-8")
                )
            except ValueError as e:
                print(e)
                with lock:
                    global_vars.command = Command.STOP
                break

            if command_recv == Command.START:
                global_vars.laptop_command.send(
                    "Raspberry Pi ready to start".encode("utf-8")
                )
                start_time_temp = float(
                    global_vars.laptop_command.recv(1024).decode("utf-8")
                )
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

            elif command_recv in (Command.STOP, Command.PAUSE):
                with lock:
                    global_vars.command = command_recv

            elif command_recv == Command.RESUME:
                with lock:
                    global_vars.command = Command.START
                    barrier.wait()

            elif command_recv == Command.MAP:
                with lock:
                    global_vars.command = Command.STOP
                select = global_vars.laptop_command.recv(1024).decode("utf-8")
                if select == Command.MAP_SELECT:
                    with lock:
                        global_vars.command = Command.MAP_SELECT
                        barrier.wait()
                    position = global_vars.laptop_command.recv(1024).decode("utf-8")
                    with open(
                        "mapping/pi_position.json", mode="w", encoding="utf-8"
                    ) as f:
                        f.write(json.dumps({"position": position}))
                    with lock:
                        global_vars.command = Command.READY

            elif command_recv == Command.STREAM:
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
