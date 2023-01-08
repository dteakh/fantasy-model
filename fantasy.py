import datetime
import time
from enum import Enum
from typing import Dict, List, NamedTuple

import requests
from bs4 import BeautifulSoup

headers = {
    "Accept":
    "*/*",
    "User-agent":
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 "
    "Safari/537.36"
}


class EventFilter(Enum):
    """ Tournaments filter for tier differentiating. """
    ALL = "ALL"
    LAN = "Lan"
    BIG = "BigEvents"
    MAJORS = "Majors"


class RankFilter(Enum):
    """ Ranking filter for stats differentiating. """
    TOP5 = 1
    TOP10 = 2
    TOP20 = 3
    TOP30 = 4


class Event(NamedTuple):
    name: str
    rank: float
    prize: int
    duration: int
    isLan: bool
    players: Dict[str, str]


def set_timeout(timeout):

    def deco(f):
        last_call = 0

        def inner(*args, **kwargs):
            nonlocal last_call
            delta = time.time() - last_call
            if delta < timeout:
                time.sleep(timeout - delta)
            last_call = time.time()
            return f(*args, **kwargs)

        return inner

    return deco


@set_timeout(0.5)
def get_tournaments(pl_id: str, pl_name: str, start: datetime.date,
                    end: datetime.date, efilter: EventFilter) -> List[str]:
    """
    Takes player's ID and nickname, start and end date as datetime, and the TFilter -- the filter for tournaments.
    Returns the list of semi-links with the player's stats on a certain tournament.

    """
    assert (start <= end <=
            datetime.date.today()), "Wrong start or end parameters passed."
    start = start.strftime("%Y-%m-%d")
    end = end.strftime("%Y-%m-%d")
    url = f"https://www.hltv.org/stats/players/events/{pl_id}/{pl_name}?startDate={start}&endDate={end}&matchType={efilter.value}"
    tournaments_page = requests.get(url, headers=headers).text
    parser = BeautifulSoup(tournaments_page, "lxml")
    processed = set()
    tournaments = []
    for block in parser.find("table", class_="stats-table").find_all(
            "img", class_="eventLogo"):
        tourney = block.find_next_sibling("a").get("href")
        if tourney not in processed:
            processed.add(tourney)
            tournaments.append(tourney)
    return tournaments


@set_timeout(0.5)
def get_event_info(event_url: str) -> Event:
    """
    Parses the given tournament URL extracting the basic information.

    :returns: an Event object containing basic parameters
    """

    def __players(source: BeautifulSoup) -> Dict[str, str]:
        """ :returns: a dictionary of players' ID and nicknames """

        players = dict()
        for team_box in source.find_all("div", class_="lineup-box hidden"):
            for pl_link in team_box.find_all("a"):
                items = pl_link.get("href").split("/")
                players[items[-2]] = items[-1].lower()
        return players

    def __rank(source: BeautifulSoup) -> float:
        """ :returns: an average rank of tournament participant """

        ranks = source.find_all("div", class_="event-world-rank")
        return 0 if not ranks else sum(int(rank.text[1:])
                                       for rank in ranks) / len(ranks)

    def __prize(table) -> int:
        """ :returns: an amount of the prize pool or 0 if not a number """

        if "$" not in table[3].text:
            return 0
        return int(table[3].text[1:].replace(",", ""))

    def __duration(table) -> int:
        """ :returns: a number of days the event lasts """

        months = {
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
        items = table[0].text.split(" ")
        start = datetime.date(int(items[2]), months[items[0]],
                              int(items[1][:-2]))
        items = table[1].text.split(" ")
        end = datetime.date(int(items[2]), months[items[0]],
                            int(items[1][:-2]))
        return int(str(end - start).split(" ")[0])

    def __isLan(table) -> bool:
        return "Online" not in table[4].text

    parser = BeautifulSoup(
        requests.get(event_url, headers=headers).text, "lxml")
    info_table = parser.find("table", class_="table eventMeta").find_all("td")
    return Event(name=event_url.split("/")[-1],
                 rank=__rank(parser),
                 prize=__prize(info_table),
                 duration=__duration(info_table),
                 isLan=__isLan(info_table),
                 players=__players(parser))
