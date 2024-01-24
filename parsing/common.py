import time
from enum import Enum


BASE = "https://www.hltv.org"
TIMEOUT = 2


def set_timeout(timeout: float):
    """ Controls the frequency of calling parsing functions. """

    def decorator(f):
        last_call = 0

        def handler(*args, **kwargs):
            nonlocal last_call
            delta = time.time() - last_call
            if delta < timeout:
                time.sleep(timeout - delta)
            last_call = time.time()
            return f(*args, **kwargs)

        return handler

    return decorator


class EventFilter(Enum):
    """ Filter for tournaments tier differentiating. """

    ALL = "ALL"
    LAN = "Lan"
    BIG = "BigEvents"
    MAJORS = "Majors"

    def __str__(self):
        return self.value


class RankingFilter(Enum):
    ALL = "ALL"
    TOP50 = "Top50"

    def __str__(self):
        return self.value


class FantasyError(Enum):
    INVALID_TIME = ValueError("Wrong time period passed.")
    INVALID_EVENT = ValueError("Wrong event key provided. Crashed in Event init.")
    NO_DATA = ValueError("No data found. Crashed in calc_pts().")
    INVALID_ARGUMENTS = ValueError("Wrong number or type of arguments passed.")

    def __str__(self):
        return self.value
