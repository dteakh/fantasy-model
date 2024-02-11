from datetime import date
from datetime import timedelta as td
from typing import Dict, List, Union

from bs4 import BeautifulSoup
from selenium import webdriver

from parsing.common import EventFilter, RankingFilter

from ._constants import TeamStat


def _get_tag(field, tag, **kwargs) -> Union[str, None]:
    if field is None:
        return None
    result = field.find(tag, **kwargs)

    if result is None:
        return None
    return result.text


# @set_timeout(TIMEOUT)
def get_stats(
    self,
    start: date = date.today() - td(weeks=12),
    end: date = date.today(),
    event: int = None,
    match: EventFilter = EventFilter.ALL,
    rank: RankingFilter = RankingFilter.ALL,
) -> Dict[str, Union[Dict[str, str], List[Dict[str, str]]]]:
    """Method collects raw statistics about team within given period and filters.
    :param start: start of period.
    :param end: end of period.
    :param event: optional, key of event to restrict statistics to.
    :param match: optional, type of events to consider (collision with 'event',
                            but this is HLTV terminology).
    :param rank: optional, matches against top-X commands to consider only.
    """

    stats = {}

    # profile
    dr = webdriver.Chrome()
    dr.get(self.get_profile_link())
    src = BeautifulSoup(dr.page_source, "html.parser")

    profile = {}
    for ts in src.find_all("div", class_="profile-team-stat"):
        stat_name = _get_tag(ts, "b")
        stat_value = _get_tag(ts, "span", class_="right")
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
        stat_name = _get_tag(ts, "div", class_="small-label-below")
        stat_value = _get_tag(ts, "div", class_="large-strong")
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
        spans = lineup.find("div", class_="lineup-year").find_all("span", class_=None)
        for span in spans:
            print(span)
            print(span.text)
        if len(spans) > 1:
            period = spans[0].text + " - " + spans[1].text
            period_unix = spans[0].get("data-unix") + " - " + spans[1].get("data-unix")
        else:
            period = spans[0].text + " - today"
            period_unix = spans[0].get("data-unix") + " - today"

        data = {"period": period, "period_unix": period_unix}

        for ts in lineup.find_all("div", class_="col standard-box big-padding"):
            stat_name = _get_tag(ts, "div", class_="small-label-below")
            stat_value = _get_tag(ts, "div", class_="large-strong")
            data[stat_name] = stat_value

        lineups.append(data)

    stats["lineups"] = lineups

    return stats
