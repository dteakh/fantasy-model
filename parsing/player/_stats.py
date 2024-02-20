from typing import Union, Dict
from datetime import date, timedelta as td

from bs4 import BeautifulSoup
from selenium import webdriver

from parsing.common import FantasyError
from parsing.player._constants import PlayerStat
from parsing.common import RankingFilter, EventFilter


def get_overview_stats(
        self,
        event_key: int = None,
        start_time: date = date.today() - td(weeks=12),
        end_time: date = date.today(),
        event_fil: EventFilter = EventFilter.ALL,
        ranking_fil: RankingFilter = RankingFilter.ALL
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
    dr.get(self.get_stat_link(stat=PlayerStat.OVERVIEW, event_key=event_key, start_time=start_time,
                              end_time=end_time, event_fil=event_fil, ranking_fil=ranking_fil))
    src = BeautifulSoup(dr.page_source, "html.parser")

    stats = src.find_all("div", class_="summaryStatBreakdownDataValue")
    assert len(stats) == 6, FantasyError.SOMETHING_WENT_WRONG
    data['rating'] = float(stats[0].text) if stats[0].text != '0.00' else None
    data['dpr'] = float(stats[1].text) if stats[1].text != '0.00' else None
    data['kast'] = float(stats[2].text[:-1]) if stats[2].text != '-' else None
    data['impact'] = float(stats[3].text) if stats[3].text != '-' else None
    data['adr'] = float(stats[4].text) if stats[4].text != '-' else None
    data['kpr'] = float(stats[5].text) if stats[5].text != '0.00' else None

    boxes = src.find_all("div", class_="col stats-rows standard-box")
    assert len(boxes) == 2, FantasyError.SOMETHING_WENT_WRONG
    stats = boxes[0].find_all("span")
    assert len(stats) == 14 or len(stats) == 10, FantasyError.SOMETHING_WENT_WRONG
    if len(stats) == 10:
        data['total_kills'] = None
        data['hs'] = None
        data['kd'] = None
        data['gdr'] = None
        data['maps_played'] = None
    else:
        data['total_kills'] = int(stats[1].text)
        data['hs'] = float(stats[3].text[:-1])
        data['kd'] = float(stats[7].text)
        data['gdr'] = float(stats[11].text)
        data['maps_played'] = int(stats[13].text)

    stats = boxes[1].find_all("span")
    assert len(stats) == 14 or len(stats) == 10, FantasyError.SOMETHING_WENT_WRONG
    if len(stats) == 10:
        data['avg_rounds_played'] = None
        data['apr'] = None
    else:
        assert data['maps_played'] is not None, FantasyError.SOMETHING_WENT_WRONG
        assert data['maps_played'] > 0, FantasyError.SOMETHING_WENT_WRONG
        data['avg_rounds_played'] = int(stats[1].text) / data['maps_played']
        data['apr'] = float(stats[5].text)

    return data


def get_individual_stats(
        self,
        event_key: int = None,
        start_time: date = date.today() - td(weeks=12),
        end_time: date = date.today(),
        event_fil: EventFilter = EventFilter.ALL,
        ranking_fil: RankingFilter = RankingFilter.ALL
) -> Dict[str, Union[int, float, None]]:
    data = {}
    dr = webdriver.Chrome()
    dr.get(self.get_stat_link(stat=PlayerStat.INDIVIDUAL, event_key=event_key, start_time=start_time,
                              end_time=end_time, event_fil=event_fil, ranking_fil=ranking_fil))
    src = BeautifulSoup(dr.page_source, "html.parser")

    rows = src.find_all("div", class_="stats-row")
    if int(rows[0].find_all("span")[1].text) == 0:
        data['opening_ratio'] = None
        data['opening_rating'] = None
        data['is_awp'] = None
    else:
        data['opening_ratio'] = float(rows[8].find_all("span")[1].text)
        data['opening_rating'] = float(rows[9].find_all("span")[1].text)
        awp_kills = int(rows[19].find_all("span")[1].text)
        rifle_kills = int(rows[18].find_all("span")[1].text)
        assert rifle_kills > 0, FantasyError.SOMETHING_WENT_WRONG
        data['is_awp'] = 1 if awp_kills / rifle_kills > 0.4 else 0

    return data


def get_clutch_stats(
        self,
        event_key: int = None,
        start_time: date = date.today() - td(weeks=12),
        end_time: date = date.today(),
        event_fil: EventFilter = EventFilter.ALL,
        ranking_fil: RankingFilter = RankingFilter.ALL
) -> Dict[str, Union[int, float, None]]:
    data = {}
    dr = webdriver.Chrome()
    print(self.get_stat_link(stat=PlayerStat.CLUTCHES, event_key=event_key, start_time=start_time,
                              end_time=end_time, event_fil=event_fil, ranking_fil=ranking_fil))
    dr.get(self.get_stat_link(stat=PlayerStat.CLUTCHES, event_key=event_key, start_time=start_time,
                              end_time=end_time, event_fil=event_fil, ranking_fil=ranking_fil))
    src = BeautifulSoup(dr.page_source, "html.parser")

    summary = src.find("div", class_="summary")
    if summary is None:
        data['1v1_wr'] = None
    else:
        values = summary.find_all("div", class_="value")
        data['1v1_wr'] = int(values[0].text) / max(1, int(values[0].text) + int(values[1].text))
        data['1v1_wr'] = round(data['1v1_wr'], 3)

    return data


def get_stats(
        self,
        event_key: int = None,
        start_time: date = date.today() - td(weeks=12),
        end_time: date = date.today(),
        event_fil: EventFilter = EventFilter.ALL,
        ranking_fil: RankingFilter = RankingFilter.ALL
) -> Dict[str, Union[int, float, None]]:
    data: Dict[str, Union[int, float, None]] = {}
    data.update(self.get_overview_stats(event_key=event_key, start_time=start_time, end_time=end_time,
                                        event_fil=event_fil, ranking_fil=ranking_fil))
    data.update(self.get_individual_stats(event_key=event_key, start_time=start_time, end_time=end_time,
                                          event_fil=event_fil, ranking_fil=ranking_fil))
    data.update(self.get_clutch_stats(event_key=event_key, start_time=start_time, end_time=end_time,
                                      event_fil=event_fil, ranking_fil=ranking_fil))

    return data
