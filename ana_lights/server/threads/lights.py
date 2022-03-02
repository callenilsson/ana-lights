"""Thread displaying pixels on the LED strip."""
import time
import threading
from ..led_strip import LEDStrip
from ...enums import Command
from .globals import command, start_time, pixels_stream, offset

# pylint: disable=broad-except
# pylint: disable=global-statement
FPS = 60


def lights_thread(
    lock: threading.Lock,
    barrier: threading.Barrier,
    strip: LEDStrip,
    video: list[list[int]],
) -> None:
    """Thread displaying pixels on the LED strip."""
    global command
    barrier.wait()
    fps = 0
    while True:
        with lock:
            get_command = command

        if get_command == Command.START:
            try:
                t = time.time()
                with lock:
                    true_index = int(abs((get_laptop_time() - start_time) * FPS))
                strip.render(video[true_index])
                fps = int(1 / (time.time() - t))
                # print(int(1/(time.time() - t)), 'fps')
            except Exception:
                with lock:
                    command = Command.STOP

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
                strip.render(pixels_stream)


def get_laptop_time() -> float:
    """Get the estimated laptop time."""
    return time.time() + offset
