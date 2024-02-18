"""
ElapsedTime is a class to measure elapsed time between start and stop events.
It can be operated directly using start and stop methods, or it can
act as a context manager in a "with" statement block.
"""
import logging
from datetime import timedelta
from time import time


class ElapsedTime:
    """Constructs ElapsedTime object, started"""

    def __init__(self, name=None):
        self.logger = logging.getLogger(self.__class__.__name__)
        if name:
            self.name = name
        else:
            self.name = repr(self)
        self._starttime = 0
        self._endtime = 0
        self._elapsed = 0
        self.start()

    def elapsed_asc(self) -> str:
        td = timedelta(seconds=self._elapsed)
        return str(td)

    def __str__(self):
        return f"{self.name=} {self._starttime=} {self._endtime=} {self._elapsed=}"

    """records start time and zeros elapsed
    if called more than once, last call wipes any previous data"""

    def start(self):
        self._starttime = time()
        self._endtime = self._starttime
        self._elapsed = 0

    """records stop time, computes and returns elapsed
    if called more than once, each call records time since last start"""

    def stop(self) -> float:
        self._endtime = time()
        self._elapsed = self._endtime - self._starttime
        return self._elapsed

    """returns elapsed time at last stop, but does not perform a stop"""

    def elapsed(self) -> float:
        return self._elapsed

    """returns time since last start, but does not perform a stop"""

    def current(self) -> float:
        return time() - self._starttime

    """translates enter "with" statement into start command"""

    def __enter__(self):
        self.start()

    """translates exit "with" statement into stop command"""

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.stop()
