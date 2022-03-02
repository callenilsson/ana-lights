"""Laptop client."""
import threading
from ..enums import Command
from .stream import stream_thread
from .raspberry_pies import RaspberryPIs
from . import global_vars


if __name__ == "__main__":
    print("Scanning for pies...")
    global_vars.initialize()
    lock = threading.Lock()
    pies = RaspberryPIs()

    while True:
        print("---------------")
        print("1 - Start")
        print("2 - Stop")
        print("3 - Pause")
        print("4 - Resume")
        print("5 - Mapping")
        print("6 - Stream")
        print("7 - Exit")
        action = input("Select an action to perform: ")

        if action == "1":
            pies.start()
        if action == "2":
            with lock:
                global_vars.command = Command.STOP
            pies.send_command(Command.STOP)
        if action == "3":
            pies.send_command(Command.PAUSE)
        if action == "4":
            pies.send_command(Command.RESUME)
        if action == "5":
            pies.map_positions()
        if action == "6":
            pies.send_command(Command.STREAM)
            threading.Thread(target=stream_thread, args=(lock, pies.pies_stream)).start()
        if action == "7":
            pies.close()
