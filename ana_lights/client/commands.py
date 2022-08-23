"""Hej."""
import time
import json
import threading
import dateutil.parser
import numpy as np
from sklearn.linear_model import LinearRegression
from ..enums import SONGS, Command
from .raspberry_pies import RaspberryPI
from . import global_vars


def send_command(lock: threading.Lock, pies: list[RaspberryPI], command: Command) -> None:
    """Send a command to the raspberry pies."""
    with lock:
        global_vars.command = command
    for pi in pies:
        pi.client.send(str(command.value).encode("utf-8"))


def map_positions(lock: threading.Lock, pies: list[RaspberryPI]) -> None:
    """Send a map position for each raspberry pi, based on its ip address."""
    # Set all raspberry pies in map mode
    send_command(lock, pies, Command.MAP)

    # Assign a position for each raspberry pi's IP
    ip_positions = {}
    for pi in pies:
        pi.client.send(Command.MAP_SELECT.value.encode("utf-8"))
        position = input("Select rpi position: ")
        pi.client.send(position.encode("utf-8"))
        ip_positions[pi.ip] = position

    # Write ip map to file
    with open("mapping/ip_positions.json", mode="w", encoding="utf-8") as f:
        f.write(json.dumps(ip_positions))


def wait_pies_ready(pies: list[RaspberryPI]) -> None:
    """Hej."""
    for pi in pies:
        command = Command(pi.client.recv(1024).decode("utf-8"))
        if command != Command.READY:
            raise ValueError(
                f"Raspberry PI sent '{command}' instead of '{Command.READY.value}'"
            )
        print("Raspberry pi ready to start", pi.ip)


def start(lock: threading.Lock, pies: list[RaspberryPI]) -> None:
    """Start raspberry pies by selecting which song or where to play from."""
    send_command(lock, pies, Command.START)

    print("---------------")
    for i, song in enumerate(SONGS):
        print(f"{i+1} - {song[0]} ({song[1]})")

    text_input = input("Enter song or custom timecode to start from: ")
    if len(text_input) == 0:
        text_input = "1"
    if text_input.isdigit():
        song = SONGS[int(text_input) - 1]
        song_start = total_seconds(song[1])
    else:
        song_start = total_seconds(text_input)

    # Send song start time to raspberry pies
    for pi in pies:
        pi.client.send(str(song_start).encode("utf-8"))

    # Wait for ready responses from RPi's
    wait_pies_ready(pies)

    # Ready
    times = []
    clicks = 4
    for i in range(clicks):
        input("Press enter to start: " + str(clicks - i))
        times.append(time.time())
    model = LinearRegression().fit(np.arange(clicks).reshape(-1, 1), times)
    start_time = model.predict([[clicks - 1]])[0]

    for pi in pies:
        pi.client.send(str(start_time).encode("utf-8"))


def total_seconds(timestamp: str) -> float:
    """Get total seconds of a timestamp string."""
    time_ = dateutil.parser.parse(timestamp).time()
    return float(
        time_.hour * 60 * 60
        + time_.minute * 60
        + time_.second
        + time_.microsecond / 1000000
    )
