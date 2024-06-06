import time
import os
from pathlib import Path
from os.path import join
from typing import Dict
from datetime import date, datetime, timedelta as td

from enum import Enum
from dataclasses import dataclass
from bs4 import BeautifulSoup, Tag

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


class Ranking(Enum):
    """Identifier for HLTV ranking pages."""

    TEAMS = "teams"

    def __str__(self):
        return self.value


@dataclass
class Config:
    start_time: date
    end_time: date
    event_fil: EventFilter
    ranking_fil: RankingFilter


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


def get_page_name(page_type: str, cfg: Config) -> str:
    """
    Maps parsed page to its name.
    :param page_type: type (name) of the page
    :param cfg: filters used to parse the page
    :returns: page name
    """
    return f"{page_type}_{str(cfg.start_time)}_{str(cfg.end_time)}_{cfg.event_fil.value}_{cfg.ranking_fil.value}.html"


def get_features_name(cfg: Config) -> str:
    """
    Maps features to object name.
    :param cfg: filters used to parse the page
    :returns: features path
    """
    return f"{str(cfg.start_time)}_{str(cfg.end_time)}_{cfg.event_fil.value}_{cfg.ranking_fil.value}.json"


def unstack_features_name(features_name: str) -> Dict[str, str]:
    fn = Path(features_name).stem
    values = fn.split("_")

    cfg = dict()
    cfg["start_time"] = datetime.strptime(values[0], "%Y-%m-%d").date()
    cfg["end_time"] = datetime.strptime(values[1], "%Y-%m-%d").date()
    cfg["event_fil"] = values[2]
    cfg["ranking_fil"] = values[3]
    return cfg


def get_ranking_page(cfg: Config, rankings_path) -> str:
    if not os.path.isdir(rankings_path):
        raise FantasyError.invalid_arguments(f"not such path {rankings_path}")

    rankings = os.listdir(rankings_path)

    end = cfg.end_time

    cnt = 0
    while f"{end}.html" not in rankings:
        end -= td(days=1)
        cnt += 1

        if cnt > 7:
            raise FantasyError.no_data(f"For given date {end} no close ranking is found.")

    return f"{end}.html"


def _read_path(path: str):
    if not os.path.isfile(path):
        raise FantasyError.invalid_arguments(f"Not found {path}")

    with open(path, "r", encoding="utf-8") as f:
        page_source = f.read()

    return BeautifulSoup(page_source, "html.parser")


def _get_src(path: str = None, src: Tag = None):
    """
    Returns bs4 Tag object, either from 'path' or already valid 'src'.
    :param path: absolute path to the overview page
    :param src: HTML/XML part of parsed tree
    :return: Tag object.
    """
    assert (path is not None or src is not None)
    if src is None:
        return _read_path(path)
    return src
