"""
mpsync is a tool that watches a folder for changes and synchronizes
them to a micropython board.

Author: Thilo Michael (uhlomuhlo@gmail.com)
"""

import time
import argparse
import os
import sys
import queue
import threading

import mp.mpfshell as mpf

from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler


class MPSync(threading.Thread):
    """
    The class that handles the the synchronizing between the folder and the MicroPython
    board.
    """

    """Number of times mpfs should try to connect to a board before giving up."""
    CONNECT_TRIES = 5

    """Protocol for mpfs to use. Maybe used in the future to support telnet connections?"""
    MPF_PROTOCOL = "ser"

    """Time to wait after filesystem changes before uploading begins."""
    WAITING_TIME = 0.5

    def __init__(self, folder=".", port="/dev/tty.SLAB_USBtoUART", verbose=False):
        super().__init__()
        self.folder = folder
        self.port = port
        self.mpfs = mpf.MpFileShell()
        self.verbose = verbose
        if not verbose:
            self.mpfs._MpFileShell__error = lambda x: None
        self.wd = None
        self._q = queue.Queue()
        self._running = False
        self._ts = 0
        self._create_watchdog()

    def _copy_file(self, file):
        dst = file.replace(self.folder, "")
        print(f"Copying {dst}")
        self.mpfs.do_put(f"{file} {dst}")

    def _create_folder(self, folder):
        dst = folder.replace(self.folder, "")
        print(f"Creating folder {dst}")
        self.mpfs.do_mkdir(dst)

    def _delete(self, path):
        dst = path.replace(self.folder, "")
        print(f"Deleting {dst}")
        self.mpfs.do_rm(dst)

    def _on_created(self, event):
        self._q.put(("CREATE", event.src_path))
        self._ts = time.time()

    def perform_create(self, src_path):
        if self.verbose:
            print(f"PERFORMING create {src_path}")
        if os.path.isfile(src_path):  # FILE
            self._copy_file(src_path)
        elif os.path.isfolder(src_path):  # FOLDER
            self._create_folder(src_path)

    def _on_deleted(self, event):
        self._q.put(("DELETE", event.src_path))
        self._ts = time.time()

    def perform_delete(self, src_path):
        if self.verbose:
            print("PERFORMING delete")
        self._delete(src_path)

    def _on_moved(self, event):
        self._q.put(("MOVE", (event.src_path, event.dest_path)))
        self._ts = time.time()

    def perform_move(self, src_path, dst_path):
        if self.verbose:
            print("PERFORMING move")
        if os.path.isfile(dst_path):
            self._delete(src_path)
            self._copy_file(dst_path)
        else:
            print("Moving folders not (yet) supported!")

    def _on_modified(self, event):
        self._q.put(("MODIFY", event.src_path))
        self._ts = time.time()

    def perform_modify(self, src_path):
        if self.verbose:
            print("PERFORMING modify")
        if os.path.isfile(src_path):
            self._copy_file(src_path)

    def _mpconnect(self):
        """Connects to a micropython board. This has to be called before copying files
        to the board."""
        if self.mpfs._MpFileShell__is_open():
            return True

        p = self.port
        if not os.path.exists(p) or os.path.isdir(p):
            print(f"Port '{p}' does not exist or is a folder!")
            return False

        for i in range(self.CONNECT_TRIES):
            self.mpfs.do_open(f"{self.MPF_PROTOCOL}:{p}")
            if self.mpfs._MpFileShell__is_open():
                return True

        print(f"Could not connect to board {p}!")
        return False

    def _mpdisconnect(self):
        """Disconnectes from the board. Has to be called to soft-reset the board.
        Preferrably after every upload."""
        if not self.mpfs._MpFileShell__is_open():
            return

        self.mpfs.do_close("")

        if self.mpfs._MpFileShell__is_open():
            print(f"Could not close connection to board {p}!")

    def _create_watchdog(self):
        """Creates a watchdog on everything in the specified folder."""
        f = self.folder

        # Abort if folder is not set
        if not os.path.exists(f) or not os.path.isdir(f):
            print(f"Path '{f}' does not exist or is not a folder!")
            sys.exit(1)

        # Create a Watchdog on the folder
        eh = PatternMatchingEventHandler("*", "", False, False)  # match everything
        eh.on_created = self._on_created
        eh.on_modified = self._on_modified
        eh.on_moved = self._on_moved
        eh.on_deleted = self._on_deleted
        self.wd = Observer()
        self.wd.schedule(eh, f, recursive=True)

    def run(self):
        waiting_time = self.WAITING_TIME
        while self._running:
            if time.time() - self._ts > waiting_time:
                q = self._q
                if not q.empty():
                    if not self._mpconnect():
                        print("Could not connect to board! Retrying in 5 seconds")
                        time.sleep(5)
                        continue
                    while not q.empty():
                        try:
                            action, params = q.get(False)
                            if action == "CREATE":
                                self.perform_create(params)
                            elif action == "DELETE":
                                self.perform_delete(params)
                            elif action == "MOVE":
                                self.perform_move(params[0], params[1])
                            elif action == "MODIFY":
                                self.perform_modify(params)
                        except queue.Empty:
                            pass
                    q.task_done()
                    self._mpdisconnect()
            time.sleep(0.1)

    def start_sync(self):
        """Starts the synchronization. Non-blocking!"""
        self.wd.start()
        self._running = True
        self.start()

    def stop_sync(self):
        """Stops the synchronization."""
        self.wd.stop()
        self._running = False


def parse_args():
    parser = argparse.ArgumentParser(
        description="A tool that continously synchronizes "
        "a folder to a MicroPython board."
    )
    parser.add_argument(
        "-f",
        "--folder",
        help="The folder that should be used to synchronize. "
        "Default is the current working directory.",
        default=None,
    )
    parser.add_argument(
        "-p",
        "--port",
        help="Serial port of the MicroPython board.",
        default="/dev/tty.SLAB_USBtoUART",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        help="Print debug information from mpfshell.",
        default=False,
        action="store_true",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    if not args.folder:
        args.folder = os.getcwd()
    mps = MPSync(folder=args.folder, port=args.port, verbose=args.verbose)
    print(f"Start syncing folder '{args.folder}' to board at '{args.port}'")
    mps.start_sync()
    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass
    mps.stop_sync()


if __name__ == "__main__":
    main()
