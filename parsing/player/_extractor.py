import re
from typing import Dict, List, Tuple, Union

import numpy as np
from bs4 import Tag
from parsing.common import FantasyError, _get_src


def extract_overview_stats(
    self, path: str, src: Tag = None
) -> Dict[str, Union[int, float, None]]:
    """
    Method collects overview stats for a player.
    :param path: absolute path to the overview page
    :param src: HTML/XML part of parsed tree
    :returns: dictionary of pairs (feature_name, feature_value)
    """
    src = _get_src(path, src)
    data = dict()

    try:
        stats = src.find_all("div", class_="summaryStatBreakdownDataValue")
        assert len(stats) == 6, FantasyError.something_went_wrong(
            f"unexpected length of stats(len={len(stats)}) found for {path}"
        )
        data["rating"] = float(stats[0].text) if stats[0].text != "0.00" else None
        data["dpr"] = float(stats[1].text) if stats[1].text != "0.00" else None
        data["kast"] = float(stats[2].text[:-1]) if stats[2].text != "-" else None
        data["impact"] = float(stats[3].text) if stats[3].text != "-" else None
        data["adr"] = float(stats[4].text) if stats[4].text != "-" else None
        data["kpr"] = float(stats[5].text) if stats[5].text != "0.00" else None
    except Exception as ex:
        data["rating"] = None
        data["dpr"] = None
        data["kast"] = None
        data["impact"] = None
        data["adr"] = None
        data["kpr"] = None
        print(f"extract_overview: {ex} occurred for {self.key}")

    try:
        boxes = src.find_all("div", class_="col stats-rows standard-box")
        stats = boxes[0].find_all("span")
        data["total_kills"] = int(stats[1].text)
        data["hs"] = float(stats[3].text[:-1])
        data["kd"] = float(stats[7].text)
        data["gdr"] = float(stats[11].text)
        data["maps_played"] = int(stats[13].text)
    except Exception as ex:
        data["total_kills"] = None
        data["hs"] = None
        data["kd"] = None
        data["gdr"] = None
        data["maps_played"] = None
        print(f"extract_overview: {ex} occurred for {self.key}")

    try:
        stats = boxes[1].find_all("span")
        data["avg_rounds_played"] = int(stats[1].text) / data["maps_played"]
        data["apr"] = float(stats[5].text)
    except Exception as ex:
        data["avg_rounds_played"] = None
        data["apr"] = None
        print(f"extract_overview: {ex} occurred for {self.key}")

    return data


def extract_individual_stats(
    self, path: str, src: Tag = None
) -> Dict[str, Union[int, float, None]]:
    """
    Method collects individual stats for a player.
    :param path: absolute path to the overview page
    :param src: HTML/XML part of parsed tree
    :returns: dictionary of pairs (feature_name, feature_value)
    """
    src = _get_src(path, src)
    data = dict()

    try:
        rows = src.find_all("div", class_="stats-row")
        data["opening_ratio"] = float(rows[8].find_all("span")[1].text)
        data["opening_rating"] = float(rows[9].find_all("span")[1].text)
        awp_kills = int(rows[19].find_all("span")[1].text)
        rifle_kills = int(rows[18].find_all("span")[1].text)
        data["is_awp"] = 1 if awp_kills / rifle_kills > 0.4 else 0
    except Exception as ex:
        data["opening_ratio"] = None
        data["opening_rating"] = None
        data["is_awp"] = None
        print(f"extract_individual: {ex} occurred for {self.key}")

    return data


def extract_clutches_stats(
    self, path: str, src: Tag = None
) -> Dict[str, Union[int, float, None]]:
    """
    Method collects clutches stats for a player.
    :param path: absolute path to the overview page
    :param src: HTML/XML part of parsed tree
    :returns: dictionary of pairs (feature_name, feature_value)
    """

    src = _get_src(path, src)
    data = dict()

    try:
        summary = src.find("div", class_="summary")
        values = summary.find_all("div", class_="value")
        data["1v1_wr"] = int(values[0].text) / max(
            1, int(values[0].text) + int(values[1].text)
        )
        data["1v1_wr"] = round(data.get("1v1_wr"), 3)
    except Exception as ex:
        data["1v1_wr"] = None
        print(f"extract_clutches: {ex} occurred for {self.key}")

    return data


def extract_matches_stats(
    self, path: str, src: Tag = None
) -> List[Tuple[bool, List[float]]]:
    """
    Method collects matches stats for a player.
    :param path: absolute path to the overview page
    :param src: HTML/XML part of parsed tree
    :returns: list of pairs (match_result, match_ratings)
    """
    src = _get_src(path, src)

    try:
        table = src.find("table", class_="stats-table")
        if table is None:
            raise FantasyError.no_data(
                f"table is None for get_overview_stats for {path}"
            )

        data = []
        current_stats = []
        current_result = None
        maps_data = table.find("tbody").find_all("tr")
        for map_data in maps_data:
            class_name = map_data.get("class")
            if class_name[-1] == "first":  # check if next match data started
                if current_result is not None:
                    data.append((current_result, current_stats))
                current_stats = []
                current_result = bool(map_data.find(class_=re.compile("match-won")))

            current_stats.append(float(map_data.find(class_=re.compile("rating")).text))

        if len(current_stats) != 0:
            data.append((current_result, current_stats))
    except Exception as ex:
        data = None
        print(f"extract_matches: {ex} occurred for {self.key}")

    return data


@staticmethod
def calculate_target(matches: List[Tuple[bool, List[float]]]) -> float:
    if not matches or len(matches) == 0:
        return np.nan

    expected_pts = 0
    for outcome, ratings in matches:
        expected_rating = sum(ratings) / max(1, len(ratings))
        print(expected_rating)
        if len(matches) > 1:
            expected_pts += (100 * (expected_rating - 1)) // 2
        else:
            expected_pts += (100 * (expected_rating - 1)) // 4

    return expected_pts / max(1, len(matches))
