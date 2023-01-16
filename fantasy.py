import datetime as dt
import time
from enum import Enum
from typing import List, Union, Dict, Tuple
import re
import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup

BASE = "https://www.hltv.org"
TIMEOUT = 1.5
HEADERS = {
    "Accept":
        "*/*",
    "User-agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 "
        "Safari/537.36"
}

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


class FantasyError(Enum):
    INVALID_TIME = ValueError("Wrong time period passed.")
    INVALID_EVENT = ValueError("Wrong event key provided. Crashed in Event init.")
    NO_DATA = ValueError("No data found. Crashed in calc_pts().")
    INVALID_ARGUMENTS = ValueError("Wrong number or type of arguments passed.")

class Player:

    def __init__(self, key: int, name: str):
        self.key = key
        self.name = name

    def __eq__(self, other):
        if isinstance(other, Player):
            return self.key == other.key
        return False

    def events_link(self, start: str, end: str) -> str:
        """ :returns: a link to the page with filtered events """

        return f"{BASE}/stats/players/events/{self.key}/{self.name}?startDate={start}&endDate={end}"

    def stats_link(self, start: str, end: str, fil: EventFilter) -> str:
        """
        Takes time period and EventFilter.
        :returns: a link to the page with matches history
         """
        return f"{BASE}/stats/players/matches/{self.key}/{self.name}?matchType={fil.value}"

    def matches_link(self, event_key: int) -> str:
        """ :returns: a link to the player's matches at a provided event"""

        return f"{BASE}/stats/players/matches/{self.key}/{self.name}?event={event_key}"

    @set_timeout(TIMEOUT)
    def get_events(self, start: dt.date, end: dt.date) -> List[int]:
        """
        Iterates through the events player played at within the provided time period and filter.
        :returns: list of events keys
        """

        if not (start <= end <= dt.date.today()):
            raise FantasyError.INVALID_TIME.value

        _url = self.events_link(start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d'))
        _src = BeautifulSoup(requests.get(_url, headers=HEADERS).text, "lxml")
        _events = []
        if _src.find("table", class_="stats-table") is not None:
            for block in _src.find("table", class_="stats-table").find_all("img", class_="eventLogo"):
                _event = int(block.find_next_sibling("a").get("href").split("=")[-1])
                if _event != 1040:
                    _events.append(int(block.find_next_sibling("a").get("href").split("=")[-1]))
        return list(set(_events))

    @set_timeout(TIMEOUT)
    def get_stats(self, start: dt.date, end: dt.date, fil: EventFilter) -> np.ndarray:
        """
        Takes (time period, EventFilter).
        :returns: a vector: (rating, winning rate)
        """

        _url = self.stats_link(start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d'), fil)
        _src = BeautifulSoup(requests.get(_url, headers=HEADERS).text, "lxml")
        _stats = _src.find("div", class_="summary").find_all("div", class_="value")

        if _stats[1].text[:-1] == "-":
            return np.zeros(2)

        return np.array([
            float(_stats[0].text),
            float(_stats[1].text[:-1])
        ])

    @set_timeout(TIMEOUT)
    def calc_pts(self, event_key: int) -> float:
        """ :returns: an amount of points earned per map at a given event """

        _url = self.matches_link(event_key)
        _src = BeautifulSoup(requests.get(_url, headers=HEADERS).text, "lxml")
        _ind_pts, _team_pts = 0, 0
        _maps = _src.find("table", class_="stats-table no-sort")
        if _maps is None or len(_maps.find("tbody").find_all("tr")) == 0:
            raise FantasyError.NO_DATA.value

        _stats = _maps.find("tbody").find_all("tr")
        for _map in _stats:
            _rating = float(_map.find(class_=re.compile("rating")).text)
            _ind_pts += int(((_rating - 1) * 100)) // 2

        _matches = _maps.find("tbody").find_all("tr", class_=re.compile("first"))
        for _match in _matches:
            _team_pts += 6 if bool(_match.find(class_=re.compile("match-won"))) else -3

        _ind_pts /= len(_stats)
        _team_pts /= len(_matches)

        return round((_ind_pts + _team_pts) / 2, 3)

    @set_timeout(TIMEOUT)
    def get_dataset(self, start: dt.date, end: dt.date, delta: dt.timedelta) -> Union[pd.DataFrame, None]:
        """
        Takes start and end date for parsing events as well as time delta for getting stats.
        :returns: a dataframe of stats or nothing if no data found
        """

        _data = []
        _cols = ["player", "event", "avg rank", "all events rating", "all events wr", "big events rating", "big events wr", "pts"]
        _types = {
            "player": np.str, "event": np.str, "all events rating": np.float32,
            "big events rating": np.float32, "all events wr": np.float32, "big events wr": np.float32, "pts": np.float32
        }

        print(f"TESTING: {self.name}")
        _events = self.get_events(start, end)

        if _events is None:
            print(f"EVENTS NOT FOUND --> {self.name}")
            return None

        for _key in _events:
            print(f"GETTING: {self.name} --> {_key}")
            try:
                _event = Event(_key)
                _pts = self.calc_pts(_key)

                _all_stats = self.get_stats(_event.start - delta, _event.start - dt.timedelta(1), EventFilter.ALL)
                _big_stats = self.get_stats(_event.start - delta, _event.start - dt.timedelta(1), EventFilter.BIG)

                _ev_data = np.array([_event.name, _event.rank])

                _data.append(np.concatenate(([self.name], [_event.name, _event.rank],
                                             _all_stats, _big_stats, [_pts]), axis=0))

            except Exception as ex:
                print(f"FAILED: {str(ex)}")
                continue

        print(f"TOTAL EVENTS: {len(_events)}")
        print(f"OK: {len(_data)}")
        print(f"FAILED: {len(_events) - len(_data)}")
        return pd.DataFrame(_data, columns=_cols).astype(_types)


class Event:

    @set_timeout(TIMEOUT)
    def __init__(self, key: int):

        self.key = key

        def _name(source: BeautifulSoup) -> str:
            return source.find("h1", class_="event-hub-title").text

        def _rank(source: BeautifulSoup) -> float:
            _ranks = source.find_all("div", class_="event-world-rank")
            return 0 if not _ranks else sum(
                int(rank.text[1:]) for rank in _ranks) / len(_ranks)

        def _dates(table) -> Tuple[dt.date, dt.date]:
            _months = {
                "Jan": 1,
                "Feb": 2,
                "Mar": 3,
                "Apr": 4,
                "May": 5,
                "Jun": 6,
                "Jul": 7,
                "Aug": 8,
                "Sep": 9,
                "Oct": 10,
                "Nov": 11,
                "Dec": 12
            }
            _items = table[0].text.split(" ")
            _start = dt.date(int(_items[2]), _months[_items[0]],
                             int(_items[1][:-2]))
            _items = table[1].text.split(" ")
            _end = dt.date(int(_items[2]), _months[_items[0]],
                           int(_items[1][:-2]))
            return _start, _end

        _src = BeautifulSoup(requests.get(self.event_info_link(), headers=HEADERS).text, "lxml")
        _table = _src.find("table", class_="table eventMeta")

        if _table is None or len(_table.find_all("td")) != 5:
            raise FantasyError.INVALID_EVENT.value

        _table = _table.find_all("td")
        self.name = _name(_src)
        self.rank = round(_rank(_src), 3)
        self.start, self.end = _dates(_table)

    def __eq__(self, other):
        if isinstance(other, Event):
            return self.key == other.key
        return False

    def event_info_link(self) -> str:
        """ :returns: a link to the event page """

        return f"https://www.hltv.org/events/{self.key}/event"

    @set_timeout(TIMEOUT)
    def get_players(self) -> List[Player]:
        """ :returns: a list of Player objects """

        src = BeautifulSoup(requests.get(self.event_info_link(), headers=HEADERS).text, "lxml")
        _result = []
        for team_box in src.find_all("div", class_="lineup-box hidden"):
            for pl_link in team_box.find_all("a"):
                _items = pl_link.get("href").split("/")
                _result.append(
                    Player(key=int(_items[-2]), name=_items[-1].lower()))
        return _result

    @set_timeout(TIMEOUT)
    def get_costs(self, file_name: str) -> Dict[str, int]:
        with open(file_name, "r") as file:
            _src = BeautifulSoup(file.read(), "lxml")
        _costs = dict()
        try:
            for box in _src.find_all("div", "teamPlayer"):
                _name = box.find("div", class_="player-card-container").text.lower()
                _cost = int(box.find("div", class_="playerButtonText").text.split(",")[0][1:])
                _costs[_name] = _cost
        except Exception as ex:
            print(f"FAILED: {str(ex)}")
            return {}
        return _costs
