import re
from datetime import datetime
from typing import Dict, List, Union

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
    data["weeks_in_top30"] = np.int32(profile["Weeks in top30 for core"])
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
    data = []
    for match in matches:
        match_data = dict()
        match_data["time"] = datetime.strptime(match["time"], "%d/%m/%y").date()
        match_data["event"] = match["event"].lower()
        match_data["opponent"] = match["opponent"].lower()
        match_data["map"] = match["map"].lower()
        match_data["result"] = match["result"].lower()

        rounds = match["rounds"].split("-")
        match_data["rounds_won"] = np.int32(rounds[0].strip())
        match_data["rounds_lost"] = np.int32(rounds[1].strip())

        data.append(match_data)

    return data


def _preprocess_events(events: List[Dict[str, str]]) -> List[Dict[str, str]]:
    data = []
    for event in events:
        event_data = dict()
        event_data["placement"] = event["placement"]
        event_data["event"] = event["event"].lower()

        data.append(event_data)

    return data


def _preprocess_lineups(lineups: List[Dict[str, str]]) -> List[Dict[str, str]]:
    data = list()

    for lineup in lineups:
        lineup_data = dict()
        lineup_data["period"] = lineup["period"].lower()
        lineup_data["period_unix"] = lineup["period_unix"].lower()
        lineup_data["maps_played"] = np.int32(lineup["Maps played"])

        matches_results = lineup["Wins / draws / losses"].split("/")
        lineup_data["wins"] = np.int32(matches_results[0].strip())
        lineup_data["draws"] = np.int32(matches_results[1].strip())
        lineup_data["losses"] = np.int32(matches_results[2].strip())
        lineup_data["lan_top3_placings"] = np.int32(lineup["LAN top 3 placings"])

        data.append(lineup_data)

    return data
