import re
from datetime import datetime, date
from typing import Dict, List, Union
from dateutil.parser import parse

import numpy as np


def preprocess_stats(
    self, stats: Dict[str, Union[Dict[str, str], List[Dict[str, str]]]]
) -> Dict[str, Union[Dict[str, str], List[Dict[str, str]]]]:
    """Applies preprocessing to raw team statistics.
    :param stats: statistics from `team._stats.get_stats` method"""
    preprocessed_stats = {
        "profile": _preprocess_profile(stats["profile"]),
        "overview": _preprocess_overview(stats["overview"]),
        "matches": _preprocess_matches(stats["matches"]),
        "events": _preprocess_events(stats["events"]),
        "lineups": _preprocess_lineups(stats["lineups"]),
    }

    return preprocessed_stats


def _preprocess_profile(profile: Dict[str, str]) -> Dict[str, str]:
    data = dict()
    data["world_ranking"] = np.int32(re.findall(r"[0-9]+", profile["World ranking"])[0])
    data["weeks_in_top30_core"] = np.int32(profile["Weeks in top30 for core"])
    data["avg_player_age"] = np.float64(profile["Average player age"])

    fullname_parts = profile["Coach"].strip().replace("'", "").split(" ")
    data["coach_nickname"] = fullname_parts[1].lower()
    data["coach_name"] = (fullname_parts[0] + " " + fullname_parts[2]).lower()

    return data


def _preprocess_overview(overview: Dict[str, str]) -> Dict[str, str]:
    data = dict()
    data["maps_played"] = np.int32(overview["Maps played"])

    matches_results = overview["Wins / draws / losses"].split("/")
    data["wins"] = np.int32(matches_results[0].strip())
    data["draws"] = np.int32(matches_results[1].strip())
    data["losses"] = np.int32(matches_results[2].strip())

    data["kills"] = np.int32(overview["Total kills"])
    data["deaths"] = np.int32(overview["Total deaths"])
    data["rounds_played"] = np.int32(overview["Rounds played"])
    data["team_kd"] = np.float64(overview["K/D Ratio"])

    return data


def _preprocess_matches(matches: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """
    Despite preprocessing, converts individual maps info into matches info.
    :param matches: this is not 'matches' played but 'maps' played.
    """
    data = []

    cur_match = dict()
    is_new_match = True
    for map_ in reversed(matches):  # iterating according to timeline
        if is_new_match:
            cur_match["opponent"] = map_["opponent"].lower()
            cur_match["date"] = datetime.strptime(map_["time"], "%d/%m/%y").date()
            cur_match["event"] = map_["event"].lower()

            cur_match["maps_played"] = 0
            cur_match["maps_won"] = 0
            cur_match["maps_lost"] = 0
            cur_match["maps_res_seq"] = ""

            cur_match["rounds_played"] = 0
            cur_match["rounds_won"] = 0
            cur_match["rounds_lost"] = 0
            cur_match["rounds_res_seq"] = ""

            cur_match["is_winner"] = None

            is_new_match = False

        cur_match["maps_played"] += 1
        cur_match["maps_won"] += int(map_["result"].lower() == "w")
        cur_match["maps_lost"] += int(map_["result"].lower() == "l")
        cur_match["maps_res_seq"] += map_["result"].lower()

        rounds = map_["rounds"].split("-")
        rounds_won = np.int32(rounds[0].strip())
        rounds_lost = np.int32(rounds[1].strip())
        cur_match["rounds_played"] += rounds_won + rounds_lost
        cur_match["rounds_won"] += rounds_won
        cur_match["rounds_lost"] += rounds_lost
        cur_match["rounds_res_seq"] += map_["rounds"].strip() + "|"

        if map_["is_last_map"]:
            cur_match["is_winner"] = int(cur_match["maps_won"] > cur_match["maps_lost"])

            data.append(cur_match.copy())  # shallow copy is enough
            is_new_match = True
            cur_match = {}

    return data


def _preprocess_events(events: List[Dict[str, str]]) -> List[Dict[str, str]]:
    data = []
    for event in events:
        event_data = dict()
        event_data["placement"] = event["placement"]
        event_data["event_filter"] = event["event_filter"]
        event_data["event"] = event["event"].lower()

        data.append(event_data)

    return data


def _preprocess_lineups(lineups: List[Dict[str, str]]) -> List[Dict[str, str]]:
    data = list()

    for lineup in lineups:
        lineup_data = dict()
        start = lineup["period"].split("-")[0].strip()
        end = lineup["period"].split("-")[1].strip()

        lineup_data["start"] = parse(start) if start != "today" else date.today()
        lineup_data["end"] = parse(end) if end != "today" else date.today()
        lineup_data["is_active"] = (end == "today")
        lineup_data["maps_played"] = np.int32(lineup["Maps played"])

        matches_results = lineup["Wins / draws / losses"].split("/")
        lineup_data["wins"] = np.int32(matches_results[0].strip())
        lineup_data["draws"] = np.int32(matches_results[1].strip())
        lineup_data["losses"] = np.int32(matches_results[2].strip())
        lineup_data["lan_top3_placings"] = np.int32(lineup["LAN top 3 placings"])

        data.append(lineup_data)

    return data
