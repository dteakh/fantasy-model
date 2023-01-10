import datetime as dt
import time
from enum import Enum
from typing import List, Union
import re

import numpy as np
import pandas as pd

import requests
from bs4 import BeautifulSoup

headers = {
    "Accept":
        "*/*",
    "User-agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 "
        "Safari/537.36"
}

_timeout = 1.0


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


class RankFilter(Enum):
    """ Filter for opponents rank differentiating. """

    ALL = "ALL"
    TOP5 = "Top5"
    TOP10 = "Top10"
    TOP20 = "Top20"
    TOP30 = "Top30"


class FantasyError(Enum):
    INVALID_TIME = ValueError("Wrong time period passed.")
    INVALID_EVENT = ValueError("Wrong event key provided.")
    NO_DATA = ValueError("No data found.")


class Player:

    def __init__(self, key: int, name: str):
        self.key = key
        self.name = name

    def __eq__(self, other):
        if isinstance(other, Player):
            return self.key == other.key
        return False

    def events_link(self, start: str, end: str, fil: EventFilter) -> str:
        """ :returns: a link to the page with filtered events """

        return f"https://www.hltv.org/stats/players/events/" \
               f"{self.key}/{self.name}?startDate={start}&endDate={end}&matchType={fil.value}"

    def stats_link(self, event_key: int, fil: RankFilter) -> str:
        """ :returns: a link to the page with stats at a provided event """

        return f"https://www.hltv.org/stats/players/{self.key}/{self.name}?event={event_key}&rankingFilter={fil.value}"

    def matches_link(self, event_key: int, fil: RankFilter) -> str:
        """ :returns: a link to the player's matches at a provided event"""

        return f"https://www.hltv.org/stats/players/" \
               f"matches/{self.key}/{self.name}?event={event_key}&rankingFilter={fil.value}"

    @set_timeout(_timeout)
    def get_events(self, start: dt.date, end: dt.date, fil: EventFilter) -> List[int]:
        """
        Iterates through the events player played at within the provided time period and filter.
        :returns: list of events keys
        """

        if not (start <= end <= dt.date.today()):
            raise FantasyError.INVALID_TIME.value
        _url = self.events_link(start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d'), fil)
        _src = BeautifulSoup(requests.get(_url, headers=headers).text, "lxml")
        _events = []
        if _src.find("table", class_="stats-table") is not None:
            for block in _src.find("table", class_="stats-table").find_all("img", class_="eventLogo"):
                _event = int(block.find_next_sibling("a").get("href").split("=")[-1])
                if _event != 1040:
                    _events.append(int(block.find_next_sibling("a").get("href").split("=")[-1]))
        return list(set(_events))

    @set_timeout(_timeout)
    def get_event_stats(self, event_key: int, fil: RankFilter) -> np.ndarray:
        """ :returns: a vector: (rating, dpr, kast, impact, adr, kpr) """

        _src = BeautifulSoup(requests.get(self.stats_link(event_key, fil), headers=headers).text, "lxml")
        _stats = _src.find_all("div", class_="summaryStatBreakdownDataValue")

        if float(_stats[0].text) == 0:
            raise FantasyError.NO_DATA.value
        return np.array([
            float(_stats[0].text),
            float(_stats[1].text),
            float(_stats[2].text[:-1]),
            float(_stats[3].text),
            float(_stats[4].text),
            float(_stats[5].text)])

    @set_timeout(_timeout)
    def calc_pts(self, event_key: int, fil: RankFilter) -> float:
        """ :returns: an amount of points earned per map at a given event """

        _url = self.matches_link(event_key, fil)
        _src = BeautifulSoup(requests.get(_url, headers=headers).text, "lxml")
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

    @set_timeout(_timeout)
    def get_dataset(self, start: dt.date, end: dt.date, fil: EventFilter) -> Union[pd.DataFrame, None]:
        _data = []
        _cols = ["player", "player_id", "event", "event_id", "major related", "lan",
                 "avg rank", "prize", "start date", "end date", "rating", "dpr", "kast", "impact", "adr", "kpr", "pts"]
        print(f"TESTING: {self.name}")
        _events = self.get_events(start, end, fil)
        if _events is None:
            print(f"EVENTS NOT FOUND --> {self.name}")
            return None

        for _key in _events:
            print(f"GETTING: {self.name} --> {_key}")
            try:
                _ev = Event(_key)
                time.sleep(1)
                _pts = self.calc_pts(_key, RankFilter.ALL)
                _ps = ["major", "rmr"]
                _event_data = [self.name, self.key, _ev.name, _ev.key,  any(p in _ev.name.lower() for p in _ps),
                               _ev.lan, _ev.rank, _ev.prize, _ev.start_date, _ev.end_date]
                _stats_data = self.get_event_stats(_ev.key, RankFilter.ALL)
                _data.append(np.concatenate((_event_data, _stats_data, [_pts]), axis=0))
            except Exception as ex:
                print(f"FAILED: {str(ex)}")
                continue
        print(f"TOTAL EVENTS: {len(_events)}")
        print(f"OK: {len(_data)}")
        print(f"FAILED: {len(_events) - len(_data)}")
        return pd.DataFrame(_data, columns=_cols)


class Event:

    @set_timeout(_timeout)
    def __init__(self, key: int):

        self.key = key

        def _name(source: BeautifulSoup) -> str:
            return source.find("h1", class_="event-hub-title").text

        def _rank(source: BeautifulSoup) -> float:
            _ranks = source.find_all("div", class_="event-world-rank")
            return 0 if not _ranks else sum(
                int(rank.text[1:]) for rank in _ranks) / len(_ranks)

        def _prize(table) -> Union[int, str]:
            return int(table[3].text[1:].replace(",", "")) if "$" in table[3].text else "Other"

        def _duration(table) -> (str, str):
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
            return _start.strftime('%Y-%m-%d'), _end.strftime('%Y-%m-%d')

        def _lan(table) -> bool:
            return "Online" not in table[4].text

        _src = BeautifulSoup(requests.get(self.event_info_link(), headers=headers).text, "lxml")
        _table = _src.find("table", class_="table eventMeta")
        if _table is None or len(_table.find_all("td")) != 5:
            raise FantasyError.INVALID_EVENT.value

        _table = _table.find_all("td")
        self.name = _name(_src)
        self.rank = round(_rank(_src), 3)
        self.prize = _prize(_table)
        _date = _duration(_table)
        self.start_date = _date[0]
        self.end_date = _date[1]
        self.lan = _lan(_table)

    def __eq__(self, other):
        if isinstance(other, Event):
            return self.key == other.key
        return False

    def event_info_link(self) -> str:
        """ :returns: a link to the event page """

        return f"https://www.hltv.org/events/{self.key}/event"

    @set_timeout(_timeout)
    def get_players(self) -> List[Player]:
        """ :returns: a list of Player objects """

        src = BeautifulSoup(requests.get(self.event_info_link(), headers=headers).text, "lxml")
        _result = []
        for team_box in src.find_all("div", class_="lineup-box hidden"):
            for pl_link in team_box.find_all("a"):
                _items = pl_link.get("href").split("/")
                _result.append(
                    Player(key=int(_items[-2]), name=_items[-1].lower()))
        return _result
