"""Thread displaying pixels on the LED strip."""
import time
import threading
from ..led_strip import LEDStrip
from ...enums import Command
from . import global_vars

# pylint: disable=broad-except
FPS = 60


def lights_thread(
    lock: threading.Lock,
    barrier: threading.Barrier,
    strip: LEDStrip,
    video: list[list[int]],
) -> None:
    """Thread displaying pixels on the LED strip."""
    barrier.wait()
    fps = 0
    while True:
        t = time.time()

        with lock:
            get_command = global_vars.command

        if get_command == Command.START:
            try:
                with lock:
                    true_index = int(
                        abs(
                            (
                                get_laptop_time()
                                - global_vars.start_time
                                + global_vars.song_start
                            )
                            * FPS
                        )
                    )
                strip.render(video[true_index])
            except Exception as e:
                with lock:
                    print(e)
                    global_vars.command = Command.STOP

        elif get_command == Command.STOP:
            print(fps, "fps")
            strip.black()
            barrier.wait()

        elif get_command == Command.READY:
            strip.black()
            strip.status(red=10, green=0, blue=0)
            barrier.wait()

        elif get_command == Command.PAUSE:
            barrier.wait()

        if get_command == Command.MAP_SELECT:
            strip.render_color(red=10, green=10, blue=10)

        if get_command == Command.STREAM:
            with lock:
                if global_vars.pixels_stream is None:
                    continue
                strip.render(global_vars.pixels_stream)

        fps = int(1 / (time.time() - t))


def get_laptop_time() -> float:
    """Get the estimated laptop time."""
    return time.time() + global_vars.offset
