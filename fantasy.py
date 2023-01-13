import datetime as dt
import time
from enum import Enum
from typing import List, Union, Dict, NamedTuple
import re

import numpy as np
import pandas as pd

import requests
from bs4 import BeautifulSoup

from sklearn.linear_model import LinearRegression

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
    INVALID_ARGUMENTS = ValueError("Wrong number or type of arguments passed.")


class Data(NamedTuple):
    """ Data object containing cost and predicted points for a player. """

    cost: int
    pts: float


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

    def stats_link(self, *args) -> str:
        """
        Takes (event key, RankFilter) or (time period, EventFilter, RankFilter).
        :returns: a link to the page with stats at a provided event or time period
         """

        if len(args) == 4:
            return f"https://www.hltv.org/stats/players/{self.key}/{self.name}?" \
                   f"startDate={args[0].strftime('%Y-%m-%d')}&endDate={args[1].strftime('%Y-%m-%d')}" \
                   f"&matchType={args[2].value}&rankingFilter={args[3].value}"
        elif len(args) == 2:
            return f"https://www.hltv.org/stats/players/{self.key}/{self.name}?" \
                   f"event={args[0]}&rankingFilter={args[1].value}"
        else:
            raise FantasyError.INVALID_ARGUMENTS.value

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
    def get_stats(self, *args) -> np.ndarray:
        """
        Takes (event key, RankFilter) or (time period, EventFilter, RankFilter).
        :returns: a vector: (rating, dpr, kast, impact, adr, kpr)
        """

        try:
            _url = self.stats_link(*args)
        except Exception as ex:
            print(str(ex))
            return np.array([])

        _src = BeautifulSoup(requests.get(_url, headers=headers).text, "lxml")
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
    def get_dataset(self, start: dt.date, end: dt.date, ev_fil: EventFilter,
                    delta: dt.timedelta, ste_fil: EventFilter, str_fil: RankFilter) -> Union[pd.DataFrame, None]:
        """
        Takes timeperiod and event filter to parse the events according to arguments. Then takes the time delta (days),
        event filter and rank filter to parse the stats using filters time delta before the event starts.
        :returns: a dataframe of stats or nothing if no data found
        """
        _data = []
        _cols = ["player", "player_id", "event", "event_id", "major related", "lan", "qual",
                 "avg rank", "prize", "duration", "rating", "dpr", "kast", "impact", "adr", "kpr", "pts"]
        _cols_types = {"player": np.str, "player_id": np.str, "event": np.str, "event_id": np.int32,
                       "major related": np.int32, "lan": np.int32, "qual": np.int32, "avg rank": np.float32,
                       "prize": np.int32, "duration": np.int32, "rating": np.float32, "dpr": np.float32,
                       "kast": np.float32, "impact": np.float32, "adr": np.float32,
                       "kpr": np.float32, "pts": np.float32}

        print(f"TESTING: {self.name}")
        _events = self.get_events(start, end, ev_fil)
        if _events is None:
            print(f"EVENTS NOT FOUND --> {self.name}")
            return None

        for _key in _events:
            print(f"GETTING: {self.name} --> {_key}")
            try:
                _ev = Event(_key)
                time.sleep(1)
                _pts = self.calc_pts(_key, RankFilter.ALL)
                _ev_data = [self.name, self.key, _ev.name, _ev.key,
                            int(any(p in _ev.name.lower() for p in ["major", "rmr"])), int(_ev.lan),
                            int(_ev.prize == 0), _ev.rank, _ev.prize, _ev.duration]
                _stats_data = self.get_stats(_ev.start_date - delta, _ev.start_date, ste_fil, str_fil)
                _data.append(np.concatenate((_ev_data, _stats_data, [_pts]), axis=0))
            except Exception as ex:
                print(f"FAILED: {str(ex)}")
                continue
        print(f"TOTAL EVENTS: {len(_events)}")
        print(f"OK: {len(_data)}")
        print(f"FAILED: {len(_events) - len(_data)}")
        return pd.DataFrame(_data, columns=_cols).astype(_cols_types)


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
            return int(table[3].text[1:].replace(",", "")) if "$" in table[3].text else 0

        def _dates(table) -> (dt.date, dt.date):
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
        _date = _dates(_table)
        self.start_date = _date[0]
        self.end_date = _date[1]
        self.duration = int(str(_date[1] - _date[0]).split(" ")[0])
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

    @set_timeout(_timeout)
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

    @set_timeout(_timeout)
    def process(self, players: List[Player], costs: Dict[str, int], start: dt.date, end: dt.date, efilter: EventFilter,
                rfilter: RankFilter, delta: dt.timedelta) -> pd.DataFrame:

        _result = []
        _cols = ["player", "cost", "predicted pts"]
        _cols_types = {"player": np.str, "cost": np.int32, "predicted pts": np.float32}
        _players_got = list(costs.keys())

        for _pl in players:
            try:
                if _pl.name not in _players_got:
                    print(f"{_pl.name} was not found in costs list.")
                    continue
                _data = _pl.get_dataset(start, end, efilter, delta, efilter, rfilter)
                _recent_stats = _pl.get_stats(end - delta, end, efilter, rfilter)
                _pred = self.predict(_recent_stats, _data)
                _result.append(np.array([_pl.name, costs[_pl.name], _pred]))
            except Exception as ex:
                print(f"FAILED: {str(ex)}")
                continue

        return pd.DataFrame(_result, columns=_cols).astype(_cols_types)

    def predict(self, pl_stats: np.ndarray, tr_data: pd.DataFrame) -> float:
        try:
            _X = np.array(tr_data.drop(columns=["player", "player_id", "event", "event_id", "pts",
                                                "prize", "qual", "duration"]).to_numpy())  # REMOVED PARAMS
            _y = np.array(tr_data['pts'])
            _model = LinearRegression()
            _model.fit(_X, _y)
            _data_vector = np.array([[
                int(any(p in self.name.lower() for p in ["major", "rmr"])), int(self.lan),
                self.rank, pl_stats[0], pl_stats[1], pl_stats[2],
                pl_stats[3], pl_stats[4], pl_stats[5]
            ]])
            _predicted = _model.predict(_data_vector)
        except Exception as ex:
            print(f"FAILED: {str(ex)}")
            return 0

        return float(_predicted[0])
