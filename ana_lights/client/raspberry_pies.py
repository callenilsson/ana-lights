"""Raspberry pi wrapper connector."""
import socket
import sys
import time
import json
import dateutil.parser
import numpy as np
from sklearn.linear_model import LinearRegression
import nmap
from ..enums import SONGS, Command, Port


class RaspberryPIs:
    """Raspberry pi wrapper connector."""

    pies_command: list[socket.socket]
    pies_stream: list[socket.socket]

    def __init__(self) -> None:
        """Initialize the raspberry pi wrapper connector."""
        found_pies = get_pies_on_network()
        self.pies_command = connect_pies(found_pies, port=Port.COMMAND.value)
        self.pies_stream = connect_pies(found_pies, port=Port.STREAM.value)

    def send_command(self, command: Command) -> None:
        """Send a command to the raspberry pies."""
        for pi in self.pies_command:
            pi.send(str(command.value).encode("utf-8"))

    def map_positions(self) -> None:
        """Send a map position for each raspberry pi, based on its ip address."""
        # Set all raspberry pies in map mode
        self.send_command(Command.MAP)

        # Assign a position for each raspberry pi's IP
        ip_positions = {}
        for pi in self.pies_command:
            pi.send(Command.MAP_SELECT.value.encode("utf-8"))
            position = input("Select rpi position: ")
            pi.send(position.encode("utf-8"))
            ip, _ = pi.getpeername()
            ip_positions[ip] = position

        # Write ip map to file
        with open("mapping/ip_positions.json", mode="w", encoding="utf-8") as f:
            f.write(json.dumps(ip_positions))

    def start(self) -> None:
        """Start raspberry pies by selecting which song or where to play from."""
        self.send_command(Command.START)

        print("---------------")
        for i, song in enumerate(SONGS):
            print(f"{i+1} - {song[0]} ({song[1]})")

        text_input = input("Enter song or custom timecode to start from: ")
        if len(text_input) == 0:
            text_input = "1"
        if text_input.isdigit():
            song = SONGS[int(text_input) - 1]
            song_start = dateutil.parser.parse(song[1]).time()
            song_start = total_seconds(song[1])
        else:
            song_start = total_seconds(text_input)

        # Wait for ready responses from RPi's
        for pi in self.pies_command:
            pi.recv(1024).decode()
            print("Raspberry pies ready to start", pi.getpeername()[0])

        # Ready
        times = []
        clicks = 5
        for i in range(clicks):
            input("Press enter to start: " + str(clicks - i))
            times.append(time.time())
        model = LinearRegression().fit(np.arange(clicks).reshape(-1, 1), times)
        start_time = model.predict(clicks - 1)[0]

        for pi in self.pies_command:
            pi.send(str(start_time).encode("utf-8"))

    def close(self) -> None:
        """Close connections to all raspberry pies."""
        for pi in self.pies_command:
            pi.close()
        for pi in self.pies_stream:
            pi.close()
        sys.exit()


def get_pies_on_network() -> list[dict[str, str]]:
    """Get all raspberry pies on the network."""
    nm = nmap.PortScanner()
    nm.scan(hosts="192.168.1.0/24", arguments="-sP")
    host_list = nm.all_hosts()
    found_pies: list[dict[str, str]] = []
    for host in host_list:
        if "mac" not in nm[host]["addresses"]:
            continue
        mac = nm[host]["addresses"]["mac"]
        vendor = nm[host]["vendor"][mac]
        if "raspberry" in vendor.lower():
            found_pies.append({"ip": host, "mac": mac})
    return found_pies


def connect_pies(found_pies: list[dict[str, str]], port: int) -> list[socket.socket]:
    """Connect to all raspberry pies."""
    pies = []
    for found_pie in found_pies:
        pi = socket.socket()
        pi.connect((found_pie["ip"], port))
        pies.append(pi)
    return pies


def total_seconds(timestamp: str) -> int:
    """Get total seconds of a timestamp string."""
    time_ = dateutil.parser.parse(timestamp).time()
    return int(
        time_.hour * 60 * 60
        + time_.minute * 60
        + time_.second
        + time_.microsecond / 10000
    )
