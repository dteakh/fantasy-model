import time
from enum import Enum

BASE = "https://www.hltv.org"
TIMEOUT = 2


def set_timeout(timeout: float):
    """Controls the frequency of calling parsing functions."""

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
    """Filter for tournaments tier differentiating."""

    ALL = "ALL"
    LAN = "Lan"
    BIG = "BigEvents"
    MAJORS = "Majors"

    def __str__(self):
        return self.value


class RankingFilter(Enum):
    """Filter for differentiating rank."""

    ALL = "ALL"
    TOP5 = "Top5"
    TOP10 = "Top10"
    TOP20 = "Top20"
    TOP30 = "Top30"
    TOP50 = "Top50"

    def __str__(self):
        return self.value


class FantasyError:

    @staticmethod
    def no_data(msg: str = ""):
        return ValueError(f"No data found: {msg}")

    @staticmethod
    def invalid_time(msg: str = ""):
        return ValueError(f"Wrong time period passed: {msg}")

    @staticmethod
    def invalid_event(msg: str = ""):
        return ValueError(f"Wrong event key passed: {msg}")

    @staticmethod
    def invalid_arguments(msg: str = ""):
        return ValueError(f"Wrong number or type of arguments passed: {msg}")

    @staticmethod
    def something_went_wrong(msg: str = ""):
        return ValueError(f"Unexpected behaviour: {msg}")
