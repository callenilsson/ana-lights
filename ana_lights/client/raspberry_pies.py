"""Hej."""
import socket
from dataclasses import dataclass
import json
import nmap
from ..enums import Port


@dataclass
class RaspberryPI:
    """Hej."""

    ip: str
    client: socket.socket


def connect_pies(port: Port, found_pies: list[str]) -> list[RaspberryPI]:
    """Connect to all raspberry pies."""
    pies: list[RaspberryPI] = []
    for found_pie in found_pies:
        try:
            pi = socket.socket()
            pi.settimeout(5)  # 10 seconds timeout
            pi.connect((found_pie, port.value))
            pies.append(
                RaspberryPI(
                    ip=found_pie,
                    client=pi,
                ),
            )
        except Exception:  # pylint: disable=broad-except
            for pie in pies:
                pie.client.close()
            break
    return pies


def read_saved_pies() -> list[str]:
    """Hej."""
    with open("mapping/pi_ips.json", mode="r", encoding="utf-8") as f:
        pi_ips = json.load(f)
    return pi_ips


def write_new_pies() -> list[str]:
    """Hej."""
    nbr_pies = int(input("Number of RPis: "))
    pi_ips = ["192.168.1." + input(f"{i+1} RPi IP: 192.168.1.") for i in range(nbr_pies)]

    # Write raspberry pi IPs to file
    with open("mapping/pi_ips.json", mode="w", encoding="utf-8") as f:
        f.write(json.dumps(pi_ips))

    return pi_ips


def scan_pies_on_network() -> list[dict[str, str]]:
    """Scan all raspberry pies on the network."""
    nm = nmap.PortScanner()

    while True:
        nm.scan(hosts="192.168.1.0/24", arguments="-sP")
        host_list = nm.all_hosts()

        found_pies: list[dict[str, str]] = []
        for host in host_list:
            print(nm[host])
            if "Raspberry" in json.dumps(nm[host]):
                found_pies.append(
                    {
                        "ip": host,
                        "mac": nm[host]["addresses"]["mac"],
                    }
                )

        if len(found_pies) == 0:
            print("---------------")
            print("No raspberry pies found on network. Scanning again...")
        else:
            print("---------------")
            print("Found raspberry pies:", found_pies)
            print("1 - Finish scan")
            print("2 - Scan again")
            action = input("Select an action to perform: ")
            if action == "1":
                # Write raspberry pi IPs to file
                with open("mapping/pi_ips.json", mode="w", encoding="utf-8") as f:
                    f.write(json.dumps(found_pies))
                return found_pies
