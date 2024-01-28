from datetime import date
from datetime import timedelta as td
from typing import Dict, Union

from bs4 import BeautifulSoup
from selenium import webdriver

from parsing.common import EventFilter, RankingFilter

from ._constants import TeamStat


def _get_tag(field, tag, class_=None, attrs=None) -> Union[str, None]:
    if field is None or field.find(tag, class_=class_, attrs=attrs) is None:
        return None

    return field.find(tag, class_=class_, attrs=attrs).text


# @set_timeout(TIMEOUT)
def get_stats(
    self,
    start: date = date.today() - td(weeks=12),
    end: date = date.today(),
    event: int = None,
    match: EventFilter = EventFilter.ALL,
    rank: RankingFilter = RankingFilter.ALL,
) -> Dict[str, Dict[str, str]]:
    stats = {}

    # profile
    dr = webdriver.Chrome()
    dr.get(self.get_profile_link())
    src = BeautifulSoup(dr.page_source, "html.parser")

    profile = {}
    for ts in src.find_all("div", class_="profile-team-stat"):
        stat_name = _get_tag(ts, "b")
        stat_value = _get_tag(ts, "span", "right")
        if stat_value is None:
            stat_value = _get_tag(ts, "a")
        profile[stat_name] = stat_value

    stats["profile"] = profile

    # overview
    dr = webdriver.Chrome()
    dr.get(
        self.get_stat_link(
            TeamStat.OVERVIEW, start=start, end=end, match=match, event=event, rank=rank
        )
    )
    src = BeautifulSoup(dr.page_source, "html.parser")

    overview = {}
    for ts in src.find_all("div", class_="col standard-box big-padding"):
        stat_name = _get_tag(ts, "div", "small-label-below")
        stat_value = _get_tag(ts, "div", "large-strong")
        overview[stat_name] = stat_value

    stats["overview"] = overview

    # matches
    dr = webdriver.Chrome()
    dr.get(
        self.get_stat_link(
            TeamStat.MATCHES, start=start, end=end, match=match, event=event, rank=rank
        )
    )
    src = BeautifulSoup(dr.page_source, "html.parser")

    matches = []
    st = src.find("table", class_="stats-table no-sort")

    for m in st.find("tbody").find_all("tr"):
        matches.append(
            {
                "time": _get_tag(m, "td", class_="time"),
                "event": _get_tag(m, "span"),
                "opponent": _get_tag(m, "td", attrs={"class": None}),
                "map": _get_tag(m.find("td", class_="statsMapPlayed"), "span"),
                "rounds": _get_tag(m, "span", class_="statsDetail"),
                "result": m.find_all("td")[-1].text,
            }
        )

    stats["matches"] = matches

    # events
    dr = webdriver.Chrome()
    dr.get(
        self.get_stat_link(
            TeamStat.EVENT_HISTORY,
            start=start,
            end=end,
            match=match,
            event=event,
            rank=rank,
        )
    )
    src = BeautifulSoup(dr.page_source, "html.parser")

    events = []
    st = src.find("table", class_="stats-table")

    for e in st.find("tbody").find_all("tr"):
        events.append(
            {
                "placement": _get_tag(e, "td", class_="statsCenterText"),
                "event": e.find_all("span")[0].text,
            }
        )

    stats["events"] = events

    # lineup
    dr = webdriver.Chrome()
    dr.get(
        self.get_stat_link(
            TeamStat.LINEUPS, start=start, end=end, match=match, event=event, rank=rank
        )
    )
    src = BeautifulSoup(dr.page_source, "html.parser")

    lineups = []

    for lineup in src.find_all("div", class_="lineup-container"):
        data = {
            "period": _get_tag(lineup, "div", class_="lineup-year"),
            "period-unix": lineup.find("div", class_="lineup-year")
            .find("span")
            .get("data-unix"),
        }

        for ts in lineup.find_all("div", class_="col standard-box big-padding"):
            stat_name = _get_tag(ts, "div", class_="small-label-below")
            stat_value = _get_tag(ts, "div", class_="large-strong")
            data[stat_name] = stat_value

        lineups.append(data)

    stats["lineups"] = lineups

    return stats
