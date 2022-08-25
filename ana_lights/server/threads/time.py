"""Thread updating the time offset to the laptop."""
import threading
import time
from typing import List
from statistics import median
import ntplib
from . import global_vars

# pylint: disable=broad-except
# pylint: disable=global-statement


def time_thread(lock: threading.Lock) -> None:
    """Thread updating the time offset to the laptop."""
    ntp_client = ntplib.NTPClient()
    ntp_samples: List[float] = []
    while True:
        # print("FPS:", global_vars.fps)
        try:
            if global_vars.laptop_ip is not None:
                response: ntplib.NTPStats = ntp_client.request(
                    host=global_vars.laptop_ip, version=4
                )

                # If there are more than 20 samples, pop the first sample
                if len(ntp_samples) > 20:
                    ntp_samples.pop(0)

                # Add ntp sample diff of rpi and laptop time to list
                ntp_samples.append(
                    (response.recv_time - response.offset) - response.orig_time
                )

                # Take median of all ntp sample diffs as the final offset
                # between rpi and laptop time
                offset = median(ntp_samples)

                with lock:
                    global_vars.offset = offset
        except Exception as e:
            print(type(e), e, "HEJ3")
        time.sleep(3)
