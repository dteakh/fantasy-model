import re
from datetime import date
from datetime import timedelta as td
from typing import Dict, List, Tuple, Union

from bs4 import BeautifulSoup
from parsing.common import EventFilter, FantasyError, RankingFilter
from parsing.player._constants import PlayerStat
from selenium import webdriver


def get_overview_stats(
    self,
    event_key: int = None,
    start_time: date = date.today() - td(weeks=12),
    end_time: date = date.today(),
    event_fil: EventFilter = EventFilter.ALL,
    ranking_fil: RankingFilter = RankingFilter.ALL,
) -> Dict[str, Union[int, float, None]]:
    """
    Method collects required stats from an overview page of the player.
    :param event_key: key of the event.
    :param start_time: start of time period.
    :param end_time: end of time period
    :param event_fil: filter events type.
    :param ranking_fil: filter opponents.
    """

    data = {}
    dr = webdriver.Chrome()
    link = self.get_stat_link(
        stat=PlayerStat.OVERVIEW,
        event_key=event_key,
        start_time=start_time,
        end_time=end_time,
        event_fil=event_fil,
        ranking_fil=ranking_fil,
    )
    dr.get(link)
    src = BeautifulSoup(dr.page_source, "html.parser")

    stats = src.find_all("div", class_="summaryStatBreakdownDataValue")
    assert len(stats) == 6, FantasyError.something_went_wrong(
        f"unexpected length of stats(1) found for event={event_key} and player={self.key}"
    )
    data["rating"] = float(stats[0].text) if stats[0].text != "0.00" else None
    data["dpr"] = float(stats[1].text) if stats[1].text != "0.00" else None
    data["kast"] = float(stats[2].text[:-1]) if stats[2].text != "-" else None
    data["impact"] = float(stats[3].text) if stats[3].text != "-" else None
    data["adr"] = float(stats[4].text) if stats[4].text != "-" else None
    data["kpr"] = float(stats[5].text) if stats[5].text != "0.00" else None

    boxes = src.find_all("div", class_="col stats-rows standard-box")
    assert len(boxes) == 2, FantasyError.something_went_wrong(
        f"unexpected boxes length found for event={event_key} and player={self.key}"
    )
    stats = boxes[0].find_all("span")
    assert len(stats) == 14 or len(stats) == 10, FantasyError.something_went_wrong(
        f"unexpected length of stats(2) found for event={event_key} and player={self.key}"
    )
    if len(stats) == 10:
        data["total_kills"] = None
        data["hs"] = None
        data["kd"] = None
        data["gdr"] = None
        data["maps_played"] = None
        raise FantasyError.no_data(
            f"crashed in get_overview_stats for event={event_key} and player={self.key}"
        )
    else:
        data["total_kills"] = int(stats[1].text)
        data["hs"] = float(stats[3].text[:-1])
        data["kd"] = float(stats[7].text)
        data["gdr"] = float(stats[11].text)
        data["maps_played"] = int(stats[13].text)

    stats = boxes[1].find_all("span")
    assert len(stats) == 14 or len(stats) == 10, FantasyError.something_went_wrong(
        f"unexpected length of stats(3) for event={event_key} and player={self.key}"
    )
    if len(stats) == 10:
        data["avg_rounds_played"] = None
        data["apr"] = None
        raise FantasyError.no_data(
            f"crashed in get_overview_stats for event={event_key} and player={self.key}"
        )
    else:
        assert data["maps_played"] is not None, FantasyError.something_went_wrong(
            f"maps_played not found for event={event_key} and player={self.key}"
        )
        assert data["maps_played"] > 0, FantasyError.something_went_wrong(
            f"maps_played is zero for event={event_key} and player={self.key}"
        )
        data["avg_rounds_played"] = int(stats[1].text) / data["maps_played"]
        data["apr"] = float(stats[5].text)

    return data


def get_individual_stats(
    self,
    event_key: int = None,
    start_time: date = date.today() - td(weeks=12),
    end_time: date = date.today(),
    event_fil: EventFilter = EventFilter.ALL,
    ranking_fil: RankingFilter = RankingFilter.ALL,
) -> Dict[str, Union[int, float, None]]:
    """
    Method collects individual stats of the player.
    :param event_key: key of the event.
    :param start_time: start of time period.
    :param end_time: end of time period
    :param event_fil: filter events type.
    :param ranking_fil: filter opponents.
    """

    data = {}
    dr = webdriver.Chrome()
    link = self.get_stat_link(
        stat=PlayerStat.INDIVIDUAL,
        event_key=event_key,
        start_time=start_time,
        end_time=end_time,
        event_fil=event_fil,
        ranking_fil=ranking_fil,
    )
    dr.get(link)
    src = BeautifulSoup(dr.page_source, "html.parser")

    rows = src.find_all("div", class_="stats-row")
    if int(rows[0].find_all("span")[1].text) == 0:
        data["opening_ratio"] = None
        data["opening_rating"] = None
        data["is_awp"] = None
        raise FantasyError.no_data(
            f"crashed in get_individual_stats for event={event_key} and player={self.key}"
        )
    else:
        data["opening_ratio"] = float(rows[8].find_all("span")[1].text)
        data["opening_rating"] = float(rows[9].find_all("span")[1].text)
        awp_kills = int(rows[19].find_all("span")[1].text)
        rifle_kills = int(rows[18].find_all("span")[1].text)
        assert rifle_kills > 0, FantasyError.something_went_wrong(
            f"rifle_kills <= 0 for for event={event_key} and player={self.key}"
        )
        data["is_awp"] = 1 if awp_kills / rifle_kills > 0.4 else 0

    return data


def get_clutch_stats(
    self,
    event_key: int = None,
    start_time: date = date.today() - td(weeks=12),
    end_time: date = date.today(),
    event_fil: EventFilter = EventFilter.ALL,
    ranking_fil: RankingFilter = RankingFilter.ALL,
) -> Dict[str, Union[int, float, None]]:
    """
    Method collects clutch stats of the player.
    :param event_key: key of the event.
    :param start_time: start of time period.
    :param end_time: end of time period
    :param event_fil: filter events type.
    :param ranking_fil: filter opponents.
    """

    data = {}
    dr = webdriver.Chrome()
    link = self.get_stat_link(
        stat=PlayerStat.CLUTCHES,
        event_key=event_key,
        start_time=start_time,
        end_time=end_time,
        event_fil=event_fil,
        ranking_fil=ranking_fil,
    )
    dr.get(link)
    src = BeautifulSoup(dr.page_source, "html.parser")

    summary = src.find("div", class_="summary")
    if summary is None:
        data["1v1_wr"] = None
        raise FantasyError.no_data(
            f"crashed in get_clutch_stats for event={event_key} and player={self.key}"
        )
    else:
        values = summary.find_all("div", class_="value")
        data["1v1_wr"] = int(values[0].text) / max(
            1, int(values[0].text) + int(values[1].text)
        )
        data["1v1_wr"] = round(data["1v1_wr"], 3)

    return data


def get_matches_stats(
    self,
    event_key: int = None,
    start_time: date = date.today() - td(weeks=12),
    end_time: date = date.today(),
    event_fil: EventFilter = EventFilter.ALL,
    ranking_fil: RankingFilter = RankingFilter.ALL,
) -> List[Tuple[bool, List[float]]]:
    """
    Method collects list of pairs (match_won, match_ratings) for specified parameters.
    :param event_key: key of the event.
    :param start_time: start of time period.
    :param end_time: end of time period
    :param event_fil: filter events type.
    :param ranking_fil: filter opponents.
    """

    dr = webdriver.Chrome()
    link = self.get_stat_link(
        stat=PlayerStat.MATCHES,
        event_key=event_key,
        start_time=start_time,
        end_time=end_time,
        event_fil=event_fil,
        ranking_fil=ranking_fil,
    )
    dr.get(link)
    src = BeautifulSoup(dr.page_source, "html.parser")

    table = src.find("table", class_="stats-table")
    if table is None:
        raise FantasyError.no_data(
            f"table is None for get_overview_stats for event={event_key} and player={self.key}"
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

    return data


def get_stats(
    self,
    event_key: int = None,
    start_time: date = date.today() - td(weeks=12),
    end_time: date = date.today(),
    event_fil: EventFilter = EventFilter.ALL,
    ranking_fil: RankingFilter = RankingFilter.ALL,
) -> Dict[str, Union[int, float, None]]:
    """
    Method collects overview, individual and clutch stats of the player.
    :param event_key: key of the event.
    :param start_time: start of time period.
    :param end_time: end of time period
    :param event_fil: filter events type.
    :param ranking_fil: filter opponents.
    """

    data: Dict[str, Union[int, float, None]] = {}
    data.update(
        self.get_overview_stats(
            event_key=event_key,
            start_time=start_time,
            end_time=end_time,
            event_fil=event_fil,
            ranking_fil=ranking_fil,
        )
    )
    data.update(
        self.get_individual_stats(
            event_key=event_key,
            start_time=start_time,
            end_time=end_time,
            event_fil=event_fil,
            ranking_fil=ranking_fil,
        )
    )
    data.update(
        self.get_clutch_stats(
            event_key=event_key,
            start_time=start_time,
            end_time=end_time,
            event_fil=event_fil,
            ranking_fil=ranking_fil,
        )
    )

    return data
