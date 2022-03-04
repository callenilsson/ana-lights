"""Thread receiving streamed pixels from the laptop."""
import json
import socket
import threading
from ...enums import Command, Port
from . import global_vars

# pylint: disable=broad-except
# pylint: disable=global-statement


def stream_thread(lock: threading.Lock) -> None:
    """Thread receiving streamed pixels from the laptop."""
    print("Starting stream thread...")
    server = socket.socket()
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("0.0.0.0", Port.STREAM.value))  # nosec
    server.listen(1)
    laptop, _ = server.accept()

    while True:
        try:
            data = laptop.recv(4096)
            data_decoded = data.decode("utf-8")
            while data_decoded[-1] != "]":
                data = laptop.recv(4096)
                data_decoded += data.decode("utf-8")

            laptop.send(Command.NEXT.value.encode("utf-8"))

        except Exception as e:
            print(e, "HEJ1")
            laptop.close()
            server.close()
            break

        with lock:
            global_vars.pixels_stream = json.loads(data_decoded)
