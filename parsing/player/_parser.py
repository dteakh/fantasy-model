import os
from datetime import date
from datetime import timedelta as td
from typing import Union

from parsing.common import EventFilter, RankingFilter
from parsing.player import PlayerStat
from selenium import webdriver


def get_page(
    self,
    page_type: PlayerStat,
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
    :param page_type: page type to parse
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
        stat=page_type,
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
