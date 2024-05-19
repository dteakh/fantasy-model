import os
from datetime import date
from datetime import timedelta as td

from typing import Union
from selenium import webdriver

from parsing.common import EventFilter, RankingFilter
from parsing.player._constants import PlayerStat


def get_overview_page(
    self,
    path: str = None,
    event_key: int = None,
    start_time: date = date.today() - td(weeks=12),
    end_time: date = date.today(),
    event_fil: EventFilter = EventFilter.ALL,
    ranking_fil: RankingFilter = RankingFilter.ALL,
    return_page: bool = False,
) -> Union[str, None]:
    """
    Method collects overview page for a player.
    :param path: saves the page to the absolute path if specified
    :param event_key: key of the event.
    :param start_time: start of time period.
    :param end_time: end of time period
    :param event_fil: filter events type.
    :param ranking_fil: filter opponents.
    :param return_page: returns page if True
    """

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
    if path:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(dr.page_source)
    if return_page:
        return dr.page_source


def get_individual_page(
    self,
    path: str = None,
    event_key: int = None,
    start_time: date = date.today() - td(weeks=12),
    end_time: date = date.today(),
    event_fil: EventFilter = EventFilter.ALL,
    ranking_fil: RankingFilter = RankingFilter.ALL,
    return_page: bool = False,
) -> Union[str, None]:
    """
    Method collects individual page of a player.
    :param path: saves the page to the absolute path if specified
    :param event_key: key of the event.
    :param start_time: start of time period.
    :param end_time: end of time period
    :param event_fil: filter events type.
    :param ranking_fil: filter opponents.
    :param return_page: returns page if True
    """

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
    if path:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(dr.page_source)

    if return_page:
        return dr.page_source


def get_clutches_page(
    self,
    path: str = None,
    event_key: int = None,
    start_time: date = date.today() - td(weeks=12),
    end_time: date = date.today(),
    event_fil: EventFilter = EventFilter.ALL,
    ranking_fil: RankingFilter = RankingFilter.ALL,
    return_page: bool = False,
) -> Union[str, None]:
    """
    Method collects clutches page of a player.
    :param path: saves the page to the absolute path if specified
    :param event_key: key of the event.
    :param start_time: start of time period.
    :param end_time: end of time period
    :param event_fil: filter events type.
    :param ranking_fil: filter opponents.
    :param return_page: returns page if True
    """

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
    if path:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(dr.page_source)

    if return_page:
        return dr.page_source


def get_matches_page(
    self,
    path: str = None,
    event_key: int = None,
    start_time: date = date.today() - td(weeks=12),
    end_time: date = date.today(),
    event_fil: EventFilter = EventFilter.ALL,
    ranking_fil: RankingFilter = RankingFilter.ALL,
    return_page: bool = False,
) -> Union[str, None]:
    """
    Method collects matches page for a player.
    :param path: saves the page to the absolute path if specified
    :param event_key: key of the event.
    :param start_time: start of time period.
    :param end_time: end of time period
    :param event_fil: filter events type.
    :param ranking_fil: filter opponents.
    :param return_page: returns page if True
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
    if path:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(dr.page_source)

    if return_page:
        return dr.page_source
