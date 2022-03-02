"""Thread listening for commands from the laptop."""
import time
import socket
import threading
import json
from .globals import command, start_time, laptop_command
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
    global command, start_time, laptop_command
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
        laptop_command, _ = server_command.accept()

        command = Command.STOP

        while True:
            try:
                command_recv = Command(laptop_command.recv(1024).decode("utf-8"))
            except ValueError as e:
                print(e)
                with lock:
                    command = Command.STOP
                break

            if command_recv == Command.START:
                laptop_command.send("Raspberry Pi ready to start".encode("utf-8"))
                start_time_temp = float(laptop_command.recv(1024).decode("utf-8"))
                with lock:
                    start_time = start_time_temp
                    if command in (Command.STOP, Command.PAUSE, Command.READY):
                        command = Command.START
                        barrier.wait()
                    else:
                        command = Command.START

            elif command_recv in (Command.STOP, Command.PAUSE):
                with lock:
                    command = command_recv

            elif command_recv == Command.RESUME:
                with lock:
                    command = Command.START
                    barrier.wait()

            elif command_recv == Command.MAP:
                with lock:
                    command = Command.STOP
                select = laptop_command.recv(1024).decode("utf-8")
                if select == Command.MAP_SELECT:
                    with lock:
                        command = Command.MAP_SELECT
                        barrier.wait()
                    position = laptop_command.recv(1024).decode("utf-8")
                    with open(
                        "mapping/pi_position.json", mode="w", encoding="utf-8"
                    ) as f:
                        f.write(json.dumps({"position": position}))
                    with lock:
                        command = Command.READY

            elif command_recv == Command.STREAM:
                with lock:
                    if command in (Command.STOP, Command.PAUSE, Command.READY):
                        command = Command.STREAM
                        barrier.wait()
                    else:
                        command = Command.STREAM
