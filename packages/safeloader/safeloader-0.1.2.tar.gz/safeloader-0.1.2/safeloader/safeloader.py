# Inspired by Marcos Mysliwiec from https://copyprogramming.com/howto/how-to-code-loading-screen

from time import sleep
from threading import Thread
from itertools import cycle
from shutil import get_terminal_size


class Loader:

    def __init__(self, desc="Loading...", end="Done!", fail="Failed", timeout=0.1):
        self.desc = desc
        self.end = end
        self.fail = fail
        self.timeout = timeout

        self._thread = Thread(target=self._animate, daemon=True)
        self.steps = ['\\', '-', '/', '|']
        self.done = False
        self.failed = False

    def start(self):
        self._thread.start()
        return self

    def _animate(self):
        for c in cycle(self.steps):
            if self.done or self.failed:
                break
            print(f"\r{self.desc}.....{c}", flush=True, end="")
            sleep(self.timeout)

    def __enter__(self):
        self.start()

    def stop(self):
        self.done = True
        cols = get_terminal_size((80, 20)).columns
        print("\r" + " " * cols, end="", flush=True)
        if self.failed:
            print(f"\r{self.desc}.....{self.fail}", flush=True)
        else:
            print(f"\r{self.desc}.....{self.end}", flush=True)

    def __exit__(self, exc_type, exc_value, tb):
        if exc_type is not None and exc_value is not None and tb is not None:
            self.failed = True
        self.stop()

    def fail_artificially(self):
        self.failed = True
        self.stop()
