"""Thread updating the time offset to the laptop."""
import threading
import time
from typing import List
from statistics import median
import ntplib
from . import global_vars

# pylint: disable=broad-except


def time_thread(lock: threading.Lock) -> None:
    """Thread updating the time offset to the laptop."""
    ntp_client = ntplib.NTPClient()
    ntp_offsets: List[float] = []
    while True:
        # print("FPS:", global_vars.fps)
        try:
            if global_vars.laptop_ip is not None:
                response: ntplib.NTPStats = ntp_client.request(
                    host=global_vars.laptop_ip, version=4
                )

                # If there are more than 20 offset samples, pop the first sample
                if len(ntp_offsets) > 20:
                    ntp_offsets.pop(0)

                # Add ntp offset between rpi and laptop time to list
                ntp_offsets.append(response.offset)

                # Take median of all ntp offsets as the final
                # between rpi and laptop time
                offset = median(ntp_offsets)

                with lock:
                    global_vars.offset = offset
        except Exception as e:
            print(type(e), e, "HEJ3")
        time.sleep(3)
