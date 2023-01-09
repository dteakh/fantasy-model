import datetime as dt
import time
from enum import Enum
from typing import List, NamedTuple, Union, Type

import requests
from bs4 import BeautifulSoup

headers = {
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


class RankFilter(Enum):
    """ Filter for opponents rank differentiating. """

    ALL = "ALL"
    TOP5 = "Top5"
    TOP10 = "Top10"
    TOP20 = "Top20"
    TOP30 = "Top30"


class PlayerStats(NamedTuple):
    """ Contains player's stats at a given event """

    rating: float
    impact: float
    dpr: float
    adr: float
    kpr: float
    kast: float


class FantasyError(Enum):
    INVALID_TIME = ValueError(
        "Wrong time period passed. Make sure end date is no earlier than start date and not "
        "later than today.")
    WRONG_EVENT_KEY = ValueError("Wrong event key provided.")
    ANOTHER_PRIZE = ValueError("The prize is not money.")
    STATS_NOT_FOUND = ValueError("No data for the provided event and filter.")


class Player:

    def __init__(self, key: int, name: str):
        self.key = key
        self.name = name

    def __eq__(self, other):
        if isinstance(other, Player):
            return self.key == other.key
        return False

    def player_events_link(self, start: str, end: str,
                           fil: EventFilter) -> str:
        """ :returns: a link to the page with filtered events """

        return f"https://www.hltv.org/stats/players/events/" \
               f"{self.key}/{self.name}?startDate={start}&endDate={end}&matchType={fil.value}"

    def player_stats_link(self, event: "Event", fil: RankFilter):
        """ :returns: a link to the page with stats at a provided event """

        return f"https://www.hltv.org/stats/players/{self.key}/{self.name}?event={event.key}&rankingFilter={fil.value}"

    @set_timeout(0.5)
    def get_events(self, start: dt.date, end: dt.date,
                   fil: EventFilter) -> List[int]:
        """
        Iterates through the events player played at within the provided time period and filter.
        :returns: list of Event keys
        """

        if not (start <= end <= dt.date.today()):
            raise FantasyError.INVALID_TIME.value

        _url = self.player_events_link(start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d'), fil)
        _src = BeautifulSoup(requests.get(_url, headers=headers).text, "lxml")
        _events = []
        for block in _src.find("table", class_="stats-table").find_all("img", class_="eventLogo"):
            _events.append(int(block.find_next_sibling("a").get("href").split("=")[-1]))
        return list(set(_events))

    @set_timeout(0.5)
    def get_event_stats(self, event: "Event",
                        fil: RankFilter) -> Union[ValueError, PlayerStats]:
        """ :returns: a PlayerStats object or error if no data found. """

        _src = BeautifulSoup(requests.get(self.player_stats_link(event, fil), headers=headers).text, "lxml")
        _stats = _src.find_all("div", class_="summaryStatBreakdownDataValue")

        if float(_stats[0].text) == 0:
            return FantasyError.STATS_NOT_FOUND.value

        return PlayerStats(rating=float(_stats[0].text),
                           dpr=float(_stats[1].text),
                           kast=float(_stats[2].text[:-1]),
                           impact=float(_stats[3].text),
                           adr=float(_stats[4].text),
                           kpr=float(_stats[5].text))


class Event:

    @set_timeout(0.5)
    def __init__(self, key: int):

        self.key = key

        def _rank(source: BeautifulSoup) -> float:

            _ranks = source.find_all("div", class_="event-world-rank")
            return 0 if not _ranks else sum(
                int(rank.text[1:]) for rank in _ranks) / len(_ranks)

        def _prize(table) -> Union[ValueError, int]:

            if "$" not in table[3].text:
                return FantasyError.ANOTHER_PRIZE.value
            return int(table[3].text[1:].replace(",", ""))

        def _duration(table) -> int:

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
            return int(str(_end - _start).split(" ")[0])

        def _isLan(table) -> bool:
            return "Online" not in table[4].text

        _src = BeautifulSoup(requests.get(self.event_info_link(), headers=headers).text, "lxml")
        _table = _src.find("table", class_="table eventMeta")
        if _table is None or len(_table.find_all("td")) != 5:
            raise FantasyError.WRONG_EVENT_KEY.value

        _table = _table.find_all("td")
        self.rank = round(_rank(_src), 3)
        self.prize = _prize(_table)
        self.duration = _duration(_table)
        self.isLan = _isLan(_table)

    def __eq__(self, other):
        if isinstance(other, Event):
            return self.key == other.key
        return False

    def __hash__(self):
        return self.key

    def event_info_link(self) -> str:
        """ :returns: a link to the event page """
        return f"https://www.hltv.org/events/{self.key}/event"

    @set_timeout(0.5)
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
