"""Thread listening for commands from the laptop."""
import time
import socket
import threading
import json
from . import global_vars
from ..led_strip import LEDStrip
from ...enums import Command, Port


def get_command(lock: threading.Lock, laptop: socket.socket) -> Command:
    """Hej."""
    try:
        command_recv = Command(laptop.recv(1024).decode("utf-8"))
        print("Received from laptop:", command_recv)
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
    """Hej."""
    if command_recv == Command.START:
        song_start_temp = float(laptop.recv(1024).decode("utf-8"))
        laptop.send(Command.READY.value.encode("utf-8"))
        start_time_temp = float(laptop.recv(1024).decode("utf-8"))
        with lock:
            global_vars.song_start = song_start_temp
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
    """Hej."""
    if command_recv in (Command.STOP, Command.PAUSE):
        with lock:
            global_vars.command = command_recv

    if command_recv == Command.RESUME:
        with lock:
            global_vars.command = Command.START
            barrier.wait()


def mapping(
    lock: threading.Lock,
    barrier: threading.Barrier,
    command_recv: Command,
    laptop: socket.socket,
    strip: LEDStrip,
) -> None:
    """Hej."""
    if command_recv == Command.MAP:
        with lock:
            global_vars.command = Command.STOP
        select = get_command(lock, laptop)
        if select == Command.MAP_SELECT:
            strip.render_color(red=10, green=10, blue=10)

            with lock:
                global_vars.command = Command.MAP_SELECT
                barrier.wait()

            position = laptop.recv(1024).decode("utf-8")
            strip.black()
            strip.status(red=10, green=10, blue=0)

            with open("mapping/pi_position.json", mode="w", encoding="utf-8") as f:
                f.write(json.dumps({"position": position}))

            del global_vars.video

            strip.status(red=0, green=0, blue=10)
            print(f"Loading strip_{position}_30fps.json ...")
            with open(
                f"final_lights/strip_{position}_30fps.json", mode="r", encoding="utf-8"
            ) as f:
                global_vars.video = json.load(f)

            with lock:
                global_vars.command = Command.READY
        else:
            raise ValueError(f"Did not receive {Command.MAP_SELECT} from laptop.")


def load_video_from_saved_position(
    lock: threading.Lock,
    command_recv: Command,
    strip: LEDStrip,
) -> None:
    """Hej."""
    if command_recv == Command.LOAD and len(global_vars.video) == 0:
        with lock:
            global_vars.command = Command.STOP

        strip.black()
        strip.status(red=10, green=10, blue=0)

        with open("mapping/pi_position.json", mode="r", encoding="utf-8") as f:
            position = json.load(f)

        del global_vars.video

        strip.status(red=0, green=0, blue=10)
        print(f"Loading strip_{position['position']}_30fps.json ...")
        with open(
            f"final_lights/strip_{position['position']}_30fps.json",
            mode="r",
            encoding="utf-8",
        ) as f:
            global_vars.video = json.load(f)

        with lock:
            global_vars.command = Command.READY


def stream(
    lock: threading.Lock,
    barrier: threading.Barrier,
    command_recv: Command,
) -> None:
    """Hej."""
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
    server = socket.socket()
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("0.0.0.0", Port.COMMAND.value))  # nosec
    server.listen(1)

    # Green status
    strip.status(red=10, green=0, blue=0)
    print("Ready")

    try:
        laptop, _ = server.accept()

        # Update globals
        with lock:
            global_vars.laptop_ip = laptop.getpeername()[0]
            global_vars.command = Command.STOP

        while True:
            command_recv = get_command(lock, laptop)
            start(lock, barrier, command_recv, laptop)
            stop_pause_resume(lock, barrier, command_recv)
            mapping(lock, barrier, command_recv, laptop, strip)
            load_video_from_saved_position(lock, command_recv, strip)
            stream(lock, barrier, command_recv)

    except Exception as e:  # pylint: disable=broad-except
        print(e, "HEJ0")
        server.close()
        laptop.close()
