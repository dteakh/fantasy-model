import datetime as dt

from typing import Dict, Tuple, List
from bs4 import BeautifulSoup
from selenium import webdriver
from players import Player
from teams import Team
from common import TIMEOUT, set_timeout


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

        dr = webdriver.Chrome()
        dr.get(self.event_info_link())
        _src = BeautifulSoup(dr.page_source, "html.parser")
        # _src = BeautifulSoup(requests.get(self.event_info_link(), headers=HEADERS).text, "html.parser")

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

        dr = webdriver.Chrome()
        dr.get(self.event_info_link())
        _src = BeautifulSoup(dr.page_source, "html.parser")
        # src = BeautifulSoup(requests.get(self.event_info_link(), headers=HEADERS).text, "html.parser")
        _result = []
        for team_box in _src.find_all("div", class_="lineup-box hidden"):
            for pl_link in team_box.find_all("a"):
                _items = pl_link.get("href").split("/")
                _result.append(
                    Player(key=int(_items[-2]), name=_items[-1].lower()))
        return _result

    @set_timeout(TIMEOUT)
    def get_teams(self, file_name: str) -> Dict[str, int]:
        ...

    @set_timeout(TIMEOUT)
    def get_costs(self, file_name: str) -> Dict[str, int]:
        with open(file_name, "r") as file:
            _src = BeautifulSoup(file.read(), "html.parser")
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