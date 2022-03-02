"""Thread receiving streamed pixels from the laptop."""
import json
import socket
import threading
from ...enums import Port
from .globals import pixels_stream

# pylint: disable=broad-except
# pylint: disable=global-statement


def stream_thread(lock: threading.Lock) -> None:
    """Thread receiving streamed pixels from the laptop."""
    print("Starting stream thread...")
    global pixels_stream
    server_stream = socket.socket()
    server_stream.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_stream.bind(("0.0.0.0", Port.STREAM.value))  # nosec
    server_stream.listen(1)
    laptop_stream, _ = server_stream.accept()

    while True:
        try:
            data = laptop_stream.recv(4096)
            laptop_stream.send("next".encode())
        except Exception:
            print("Connection lost, shutting off stream thread...")
            break
        with lock:
            pixels_stream = json.loads(data.decode("utf-8"))
