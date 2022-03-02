"""Raspberry pi wrapper connector."""
import socket
import sys
import time
import json
from dataclasses import dataclass
from typing import List, Dict
import dateutil.parser
import numpy as np
from sklearn.linear_model import LinearRegression
import nmap
from ..enums import SONGS, Command, Port


@dataclass
class RaspberryPI:
    """"""

    ip: str
    client: socket.socket


class RaspberryPIs:
    """Raspberry pi wrapper connector."""

    pies_command: List[RaspberryPI]
    pies_stream: List[RaspberryPI]

    def __init__(self) -> None:
        """Initialize the raspberry pi wrapper connector."""
        found_pies = get_pies_on_network()
        self.pies_command = self.connect_pies(Port.COMMAND, found_pies)
        self.pies_stream = self.connect_pies(Port.STREAM, found_pies)

    def send_command(self, command: Command) -> None:
        """Send a command to the raspberry pies."""
        for pi in self.pies_command:
            pi.client.send(str(command.value).encode("utf-8"))

    def map_positions(self) -> None:
        """Send a map position for each raspberry pi, based on its ip address."""
        # Set all raspberry pies in map mode
        self.send_command(Command.MAP)

        # Assign a position for each raspberry pi's IP
        ip_positions = {}
        for pi in self.pies_command:
            pi.client.send(Command.MAP_SELECT.value.encode("utf-8"))
            position = input("Select rpi position: ")
            pi.client.send(position.encode("utf-8"))
            ip_positions[pi.ip] = position

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
            command = Command(pi.client.recv(1024).decode("utf-8"))
            if command != Command.READY:
                raise ValueError(
                    f"Raspberry PI sent '{command}' instead of '{Command.READY.value}'"
                )
            print("Raspberry pies ready to start", pi.ip)

        # Ready
        times = []
        clicks = 5
        for i in range(clicks):
            input("Press enter to start: " + str(clicks - i))
            times.append(time.time())
        model = LinearRegression().fit(np.arange(clicks).reshape(-1, 1), times)
        start_time = model.predict(clicks - 1)[0]

        for pi in self.pies_command:
            pi.client.send(str(start_time).encode("utf-8"))

    def close(self) -> None:
        """Close connections to all raspberry pies."""
        for pi in self.pies_command:
            pi.client.close()
        for pi in self.pies_stream:
            pi.client.close()
        sys.exit()

    def connect_pies(
        self, port: Port, found_pies: List[Dict[str, str]]
    ) -> List[RaspberryPI]:
        """Connect to all raspberry pies."""
        pies: List[RaspberryPI] = []
        for found_pie in found_pies:
            pi = socket.socket()
            pi.connect((found_pie["ip"], port.value))
            pies.append(
                RaspberryPI(
                    ip=found_pie["ip"],
                    client=pi,
                ),
            )
        return pies


def get_pies_on_network() -> List[Dict[str, str]]:
    """Get all raspberry pies on the network."""
    nm = nmap.PortScanner()
    nm.scan(hosts="192.168.1.0/24", arguments="-sP")
    host_list = nm.all_hosts()
    found_pies: List[Dict[str, str]] = []
    for host in host_list:
        host_name = nm[host]["hostnames"][0]["name"]
        if "raspberry" in host_name:
            found_pies.append({"ip": host})
    print("Found pies:", found_pies)
    return found_pies


def total_seconds(timestamp: str) -> int:
    """Get total seconds of a timestamp string."""
    time_ = dateutil.parser.parse(timestamp).time()
    return int(
        time_.hour * 60 * 60
        + time_.minute * 60
        + time_.second
        + time_.microsecond / 10000
    )
