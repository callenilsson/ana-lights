"""Thread updating the time offset to the laptop."""
import threading
import time
import ntplib
from . import global_vars

# pylint: disable=broad-except
# pylint: disable=global-statement


def time_thread(lock: threading.Lock) -> None:
    """Thread updating the time offset to the laptop."""
    c = ntplib.NTPClient()
    while True:
        try:
            if global_vars.laptop_ip is not None:
                response = c.request(
                    host=global_vars.laptop_ip,
                    version=4,
                )
                with lock:
                    global_vars.offset = response.offset
        except Exception as e:
            print(e, "HEJ3")
        time.sleep(1)
