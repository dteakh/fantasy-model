import os
import re
from typing import Any, Dict, List, Union

from bs4 import BeautifulSoup
from parsing.common import EventFilter, FantasyError
from parsing.player import Player


def _get_tag(field, tag, **kwargs) -> Union[str, None]:
    if field is None:
        return None
    result = field.find(tag, **kwargs)

    if result is None:
        return None
    return result.text


def _read_path(path: str):
    if not os.path.isfile(path):
        raise FantasyError.invalid_arguments(f"Not found {path}")

    with open(path, "r", encoding="utf-8") as f:
        page_source = f.read()

    return BeautifulSoup(page_source, "html.parser")


def _prep_team_name(name):
    name = name.lower()
    name = re.sub(pattern=r"[-_^*]+", repl=" ", string=name)
    name = name.strip()

    return name


def extract_profile(self, path: str) -> Dict[str, Dict[str, Any]]:
    src = _read_path(path)

    profile = {}
    for ts in src.find_all("div", class_="profile-team-stat"):
        stat_name = _get_tag(ts, "b")
        stat_value = _get_tag(ts, "span", class_="right")
        if stat_value is None:
            stat_value = _get_tag(ts, "a")
        profile[stat_name] = stat_value

    return {"profile": profile}


def extract_ranking(self, path: str, team_name: str) -> Dict[str, Dict[str, Any]]:
    src = _read_path(path)

    ranking = {}
    for team in src.find_all("div", class_="ranked-team standard-box"):
        cur_name = _get_tag(team, "span", class_="name").lower()
        if _prep_team_name(team_name) == _prep_team_name(cur_name):
            ranking["points"] = _get_tag(team, "span", class_="points")
            ranking["world_ranking"] = _get_tag(team, "span", class_="position")
            ranking["ranking_change"] = _get_tag(team, "div", class_="change")
            # ranking['players'] = []

            # for player in team.find_all("td", class_="player-holder"):
            #     placeholder = player.find("a", class_="pointer")
            #     line = placeholder.get("href", f"/player/{None}/{None}")
            #
            #     key, name = int(line.split('/')[2]), line.split('/')[3].lower()
            #         ranking['players'].append(Player(key=key, name=name))

            return {"ranking": ranking}

    ranking["points"] = None
    ranking["world_ranking"] = None
    ranking["ranking_change"] = None

    return {"ranking": ranking}


def extract_overview(self, path: str) -> Dict[str, Dict[str, Any]]:
    src = _read_path(path)

    overview = {}
    for ts in src.find_all("div", class_="col standard-box big-padding"):
        stat_name = _get_tag(ts, "div", class_="small-label-below")
        stat_value = _get_tag(ts, "div", class_="large-strong")
        overview[stat_name] = stat_value

    return {"overview": overview}


def extract_matches(self, path: str) -> Dict[str, List[Dict[str, Any]]]:
    src = _read_path(path)

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
                "is_last_map": 1 if "first" in m.get("class") else 0,
            }
        )

    return {"matches": matches}


def extract_events(
    self, path: str, match: EventFilter
) -> Dict[str, List[Dict[str, Any]]]:
    src = _read_path(path)

    events = []
    st = src.find("table", class_="stats-table")

    for e in st.find("tbody").find_all("tr"):
        events.append(
            {
                "placement": _get_tag(e, "td", class_="statsCenterText"),
                "event": e.find_all("span")[0].text,
                "event_filter": match,  # used later
            }
        )

    return {"events": events}


def extract_lineups(self, path: str) -> Dict[str, List[Dict[str, Any]]]:
    src = _read_path(path)

    lineups = []
    for lineup in src.find_all("div", class_="lineup-container"):
        spans = lineup.find("div", class_="lineup-year").find_all("span", class_=None)
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

        players = []
        for player in lineup.find_all("div", class_="teammate-info standard-box"):
            line = player.find("a", class_="image-and-label").get("href")
            if line is None:
                players.append(None)
            else:
                key = line.split("/")[3]
                name = line.split("/")[4].split("?")[0]
                players.append(Player(key=int(key.strip()), name=name.strip().lower()))

        data["players"] = players

        lineups.append(data)

    return {"lineups": lineups}
