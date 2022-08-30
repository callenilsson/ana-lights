"""Thread listening for commands from the laptop."""
import time
import socket
import threading
import json
from typing import List
import numpy as np
from . import global_vars
from ..led_strip import LEDStrip
from ...color import Color
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

            # Get position from laptop
            position = laptop.recv(1024).decode("utf-8")

            # Write position to file
            with open("mapping/pi_position.json", mode="w", encoding="utf-8") as f:
                f.write(json.dumps({"position": position}))

            # Load video at position
            load_video(lock, position, strip)

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

        # Read position from file
        with open("mapping/pi_position.json", mode="r", encoding="utf-8") as f:
            position = json.load(f)

        # Load video at position
        load_video(lock, position["position"], strip)

        with lock:
            global_vars.command = Command.READY


def load_video(lock: threading.Lock, position: str, strip: LEDStrip) -> None:
    """Hej."""
    # Set strip status to yellow
    strip.status(red=10, green=10, blue=0)

    # Remove old video from RAM
    with lock:
        del global_vars.video

    # Read number of lines (frames) in video file
    nbr_lines = 0
    with open(file=f"final_lights/strip_{position}.txt", mode="r", encoding="utf-8") as f:
        for i, _ in enumerate(f):
            # Skip every other frame to only get 30 fps
            if i % 2 == 0:
                continue
            nbr_lines += 1
    print("Will read", nbr_lines, "lines from video file")

    # Initialize video list
    video: List[List[int]] = [[]] * nbr_lines

    # Load video from file
    count = 0
    with open(file=f"final_lights/strip_{position}.txt", mode="r", encoding="utf-8") as f:
        for i, line in enumerate(f):  # type: ignore
            # Skip every other frame to only get 30 fps
            if i % 2 == 0:
                continue

            # Render load progress on strip
            if count % int(nbr_lines / 100) == 0:
                percent = count / nbr_lines

                progress_pixels = np.zeros(strip.led_count)
                progress_pixels[: int(percent * int(strip.led_count / 2))] = 1
                progress_pixels[
                    int(strip.led_count / 2) : int(strip.led_count / 2)  # noqa
                    + int(percent * int(strip.led_count / 2))
                ] = 1

                strip.render(
                    pixels=[
                        Color(red=0, green=0, blue=int(10 * val))
                        for val in progress_pixels[::-1]
                    ]
                )
            video[count] = json.loads(line)  # type: ignore
            count += 1

    # Update global video variable
    with lock:
        global_vars.video = video

    # Set strip status to green
    strip.status(red=10, green=0, blue=0)


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
        print(type(e), e, "HEJ0")
        server.close()
        laptop.close()
