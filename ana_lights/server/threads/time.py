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
        # print("FPS:", global_vars.fps)
        try:
            if global_vars.laptop_ip is not None:
                response = c.request(
                    host=global_vars.laptop_ip,
                    version=4,
                )
                laptop_time = response.recv_time - response.offset

                with lock:
                    global_vars.offset = time.time() - laptop_time
        except Exception as e:
            print(type(e), e, "HEJ3")
        time.sleep(5)
