"""Laptop client."""
import threading
from ..enums import Command, Port
from .stream import stream_thread, set_stream_window
from .raspberry_pies import read_saved_pies, scan_pies_on_network, connect_pies, close
from .commands import start, send_command, map_positions
from . import global_vars


if __name__ == "__main__":  # noqa
    print("Scanning for ..")
    global_vars.initialize()
    lock = threading.Lock()

    while True:
        found_pies = read_saved_pies()
        print("Saved RPi IPs:", found_pies)
        print("1 - Connect to saved RPi IPs")
        print("2 - Scan network for new RPi IPs")
        action = input("Select an action to perform: ")
        if action == "2":
            found_pies = scan_pies_on_network()
        pies_command = connect_pies(Port.COMMAND, found_pies)
        pies_stream = connect_pies(Port.STREAM, found_pies)

        if len(pies_command) != len(found_pies) or len(pies_stream) != len(found_pies):
            print("Could not connect to all RPis. Please re-scan for new RPi IPs.")
            continue
        break

    while True:
        print("---------------")
        print("1 - Start")
        print("2 - Stop")
        print("3 - Pause")
        print("4 - Resume")
        print("5 - Mapping")
        print("6 - Stream")
        print("7 - Stream window")
        print("8 - Exit")
        action = input("Select an action to perform: ")

        if action == "1":
            start(lock, pies_command)
        if action == "2":
            send_command(lock, pies_command, Command.STOP)
        if action == "3":
            send_command(lock, pies_command, Command.PAUSE)
        if action == "4":
            send_command(lock, pies_command, Command.RESUME)
        if action == "5":
            map_positions(lock, pies_command)
        if action == "6":
            send_command(lock, pies_command, Command.STREAM)
            threading.Thread(target=stream_thread, args=(lock, pies_stream)).start()
        if action == "7":
            set_stream_window()
        if action == "8":
            close(pies_command)
            close(pies_stream)
