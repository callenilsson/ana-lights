"""Thread updating the time offset to the laptop."""
import threading
import time
import ntplib
from .globals import laptop_command, offset

# pylint: disable=broad-except
# pylint: disable=global-statement


def time_thread(lock: threading.Lock) -> None:
    """Thread updating the time offset to the laptop."""
    global offset
    c = ntplib.NTPClient()
    while True:
        try:
            if laptop_command:
                response = c.request(laptop_command.getpeername()[0], version=4)
                with lock:
                    offset = response.offset
        except Exception as e:
            print(e)
        time.sleep(1)
