import os.path
import re
from typing import Dict, List, Tuple, Union

from bs4 import BeautifulSoup
from parsing.common import FantasyError


def extract_overview_stats(self, path: str) -> Dict[str, Union[int, float, None]]:
    """
    Method collects overview stats for a player.
    :param path: absolute path to the overview page
    :returns: dictionary of pairs (feature_name, feature_value)
    """

    if not os.path.isfile(path):
        raise FantasyError.invalid_arguments(f"Not found {path}")

    with open(path, "r", encoding="utf-8") as f:
        page_data = f.read()

    data = dict()
    src = BeautifulSoup(page_data, "html.parser")

    stats = src.find_all("div", class_="summaryStatBreakdownDataValue")
    assert len(stats) == 6, FantasyError.something_went_wrong(
        f"unexpected length of stats(1) found for {path}"
    )
    data["rating"] = float(stats[0].text) if stats[0].text != "0.00" else None
    data["dpr"] = float(stats[1].text) if stats[1].text != "0.00" else None
    data["kast"] = float(stats[2].text[:-1]) if stats[2].text != "-" else None
    data["impact"] = float(stats[3].text) if stats[3].text != "-" else None
    data["adr"] = float(stats[4].text) if stats[4].text != "-" else None
    data["kpr"] = float(stats[5].text) if stats[5].text != "0.00" else None

    boxes = src.find_all("div", class_="col stats-rows standard-box")
    assert len(boxes) == 2, FantasyError.something_went_wrong(
        f"unexpected boxes length found for {path}"
    )
    stats = boxes[0].find_all("span")
    assert len(stats) == 14 or len(stats) == 10, FantasyError.something_went_wrong(
        f"unexpected length of stats(2) found for {path}"
    )
    if len(stats) == 10:
        data["total_kills"] = None
        data["hs"] = None
        data["kd"] = None
        data["gdr"] = None
        data["maps_played"] = None
        raise FantasyError.no_data(f"crashed in get_overview_stats for {path}")
    else:
        data["total_kills"] = int(stats[1].text)
        data["hs"] = float(stats[3].text[:-1])
        data["kd"] = float(stats[7].text)
        data["gdr"] = float(stats[11].text)
        data["maps_played"] = int(stats[13].text)

    stats = boxes[1].find_all("span")
    assert len(stats) == 14 or len(stats) == 10, FantasyError.something_went_wrong(
        f"unexpected length of stats(3) for {path}"
    )
    if len(stats) == 10:
        data["avg_rounds_played"] = None
        data["apr"] = None
        raise FantasyError.no_data(f"crashed in get_overview_stats for {path}")
    else:
        assert data["maps_played"] is not None, FantasyError.something_went_wrong(
            f"maps_played not found for {path}"
        )
        assert data["maps_played"] > 0, FantasyError.something_went_wrong(
            f"maps_played is zero for {path}"
        )
        data["avg_rounds_played"] = int(stats[1].text) / data["maps_played"]
        data["apr"] = float(stats[5].text)

    return data


def extract_individual_stats(self, path: str) -> Dict[str, Union[int, float, None]]:
    """
    Method collects individual stats for a player.
    :param path: absolute path to the overview page
    :returns: dictionary of pairs (feature_name, feature_value)
    """

    if not os.path.isfile(path):
        raise FantasyError.invalid_arguments(f"Not found {path}")

    with open(path, "r", encoding="utf-8") as f:
        page_data = f.read()

    data = dict()
    src = BeautifulSoup(page_data, "html.parser")

    rows = src.find_all("div", class_="stats-row")
    if int(rows[0].find_all("span")[1].text) == 0:
        data["opening_ratio"] = None
        data["opening_rating"] = None
        data["is_awp"] = None
        raise FantasyError.no_data(f"crashed in get_individual_stats for {path}")
    else:
        data["opening_ratio"] = float(rows[8].find_all("span")[1].text)
        data["opening_rating"] = float(rows[9].find_all("span")[1].text)
        awp_kills = int(rows[19].find_all("span")[1].text)
        rifle_kills = int(rows[18].find_all("span")[1].text)
        assert rifle_kills > 0, FantasyError.something_went_wrong(
            f"rifle_kills <= 0 for {path}"
        )
        data["is_awp"] = 1 if awp_kills / rifle_kills > 0.4 else 0

    return data


def extract_clutches_stats(self, path: str) -> Dict[str, Union[int, float, None]]:
    """
    Method collects clutches stats for a player.
    :param path: absolute path to the overview page
    :returns: dictionary of pairs (feature_name, feature_value)
    """

    if not os.path.isfile(path):
        raise FantasyError.invalid_arguments(f"Not found {path}")

    with open(path, "r", encoding="utf-8") as f:
        page_data = f.read()

    data = dict()
    src = BeautifulSoup(page_data, "html.parser")

    summary = src.find("div", class_="summary")
    if summary is None:
        data["1v1_wr"] = None
        raise FantasyError.no_data(f"crashed in get_clutch_stats for {path}")
    else:
        values = summary.find_all("div", class_="value")
        data["1v1_wr"] = int(values[0].text) / max(
            1, int(values[0].text) + int(values[1].text)
        )
        data["1v1_wr"] = round(data.get("1v1_wr"), 3)

    return data


def extract_matches_stats(self, path: str) -> List[Tuple[bool, List[float]]]:
    """
    Method collects matches stats for a player.
    :param path: absolute path to the overview page
    :returns: list of pairs (match_result, match_ratings)
    """

    if not os.path.isfile(path):
        raise FantasyError.invalid_arguments(f"Not found {path}")

    with open(path, "r", encoding="utf-8") as f:
        page_data = f.read()

    src = BeautifulSoup(page_data, "html.parser")

    table = src.find("table", class_="stats-table")
    if table is None:
        raise FantasyError.no_data(f"table is None for get_overview_stats for {path}")

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

    return data
