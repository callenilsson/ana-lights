"""Laptop client."""
import threading
from ..enums import Command, Port
from .stream import stream_thread, set_stream_window
from .raspberry_pies import read_saved_pies, write_new_pies, connect_pies
from .commands import start, send_command, map_positions
from . import global_vars


if __name__ == "__main__":  # noqa
    global_vars.initialize()
    lock = threading.Lock()

    while True:
        found_pies = read_saved_pies()
        print("---------------")
        print("Saved RPi IPs:", found_pies)
        print("1 - Connect to saved RPi IPs")
        print("2 - Write new RPi IPs")
        action = input("Select an action to perform: ")
        if action == "2":
            found_pies = write_new_pies()
        pies_command = connect_pies(Port.COMMAND, found_pies)
        pies_stream = connect_pies(Port.STREAM, found_pies)

        if len(pies_command) != len(found_pies) or len(pies_stream) != len(found_pies):
            print("Could not connect to all RPis. Please re-scan for new RPi IPs.")
            continue
        break

    print("---------------")
    print("Connected to RPi IPs:", found_pies)

    if action == "2":
        map_positions(lock, pies_command)

    while True:
        print("---------------")
        print("1 - Start")
        print("2 - Stop")
        print("3 - Pause")
        print("4 - Resume")
        print("5 - Mapping")
        print("6 - Stream")
        print("7 - Stream window")
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
            set_stream_window(lock)
