import datetime as dt
from typing import List, Union, Tuple
import re
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from event import Event
from common import (
    EventFilter,
    set_timeout,
    FantasyError,
    BASE,
    TIMEOUT
)


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
        return f"{BASE}/stats/players/matches/{self.key}/{self.name}?startDate={start}&endDate={end}" \
               f"&matchType={fil.value}&rankingFilter=Top50"
 
    def matches_link(self, event_key: int) -> str:
        """ :returns: a link to the player's matches at a provided event"""
 
        return f"{BASE}/stats/players/matches/{self.key}/{self.name}?event={event_key}&rankingFilter=Top50"
 
    @set_timeout(TIMEOUT)
    def get_events(self, start: dt.date, end: dt.date) -> List[int]:
        """
        Iterates through the events player played at within the provided time period and filter.
        :returns: list of events keys
        """
 
        if not (start <= end <= dt.date.today()):
            raise FantasyError.INVALID_TIME.value
 
        _url = self.events_link(start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d'))
 
        dr = webdriver.Chrome()
        dr.get(_url)
        _src = BeautifulSoup(dr.page_source, "html.parser")
        # _src = BeautifulSoup(requests.get(_url, headers=HEADERS).text, "html.parser")
        _events = []
        if _src.find("table", class_="stats-table") is not None:
            for block in _src.find("table", class_="stats-table").find_all("img", class_="eventLogo"):
                _event = int(block.find_next_sibling("a").get("href").split("=")[-1])
                if _event != 1040:
                    _events.append(int(block.find_next_sibling("a").get("href").split("=")[-1]))
        return list(set(_events))
 
    @set_timeout(TIMEOUT)
    def get_stats(self, start: dt.date, end: dt.date, fil: EventFilter) -> Tuple[float, float]:
        """
        Takes (time period, EventFilter).
        :returns: rating
        """
 
        _url = self.stats_link(start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d'), fil)
 
        dr = webdriver.Chrome()
        dr.get(_url)
        _src = BeautifulSoup(dr.page_source, "html.parser")
        # _src = BeautifulSoup(requests.get(_url, headers=HEADERS).text, "html.parser")
        _stats = _src.find("div", class_="summary").find_all("div", class_="value")
 
        if not bool(_stats[1].text[:-1]):
            return 0, 0
 
        return float(_stats[0].text), float(_stats[1].text[:-1])
 
    @set_timeout(TIMEOUT)
    def calc_pts(self, event_key: int) -> float:
        """ :returns: an amount of points earned per map at a given event """
 
        _url = self.matches_link(event_key)
        dr = webdriver.Chrome()
        dr.get(_url)
        _src = BeautifulSoup(dr.page_source, "html.parser")
        # _src = BeautifulSoup(requests.get(_url, headers=HEADERS).text, "html.parser")
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
 
        return round(_ind_pts + _team_pts, 3)
 
    @set_timeout(TIMEOUT)
    def get_dataset(self, start: dt.date, end: dt.date, delta: dt.timedelta) -> Union[pd.DataFrame, None]:
        """
        Takes start and end date for parsing events as well as time delta for getting stats.
        :returns: a dataframe of stats or nothing if no data found
        """
 
        _data = []
        _cols = ["player", "event", "avg rank", "all events rating", "big events rating", "all events wr", "big events wr", "pts"]
        _types = {
            "player": str, "event": str, "avg rank": np.float32,
            "all events rating": np.float32, "big events rating": np.float32,
            "all events wr": np.float32, "big events wr": np.float32, "pts": np.float32
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
 
                if _event.rank > 45:
                    continue
 
                _pts = self.calc_pts(_key)
                _all_rating, _all_wr = self.get_stats(_event.start - delta, _event.start - dt.timedelta(1), EventFilter.ALL)
                _big_rating, _big_wr = self.get_stats(_event.start - delta, _event.start - dt.timedelta(1), EventFilter.BIG)
 
                _ev_data = np.array([_event.name, _event.rank])
                print(f"rating: {_all_rating} / {_big_rating} wr: {_all_wr} / {_big_wr}")
                _data.append(np.array([self.name, _event.name, _event.rank, _all_rating, _big_rating, _all_wr, _big_wr, _pts]))
 
            except Exception as ex:
                print(f"FAILED: {str(ex)}")
                continue
 
        print(f"TOTAL EVENTS: {len(_events)}")
        print(f"OK: {len(_data)}")
        print(f"FAILED: {len(_events) - len(_data)}")
        return pd.DataFrame(_data, columns=_cols).astype(_types)
