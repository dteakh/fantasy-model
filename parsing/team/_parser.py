import os
from datetime import date, datetime
from datetime import timedelta as td
from typing import Union

from parsing.common import EventFilter, FantasyError, Ranking, RankingFilter
from parsing.team._constants import TeamProfile, TeamStat
from parsing.team._utils import _is_enum_instance
from selenium import webdriver


def get_page(
    self,
    page_type: Union[TeamStat, TeamProfile, Ranking],
    start: date = date.today() - td(weeks=12),
    end: date = date.today(),
    event: int = None,
    match: EventFilter = EventFilter.ALL,
    rank: RankingFilter = RankingFilter.ALL,
    data_path: str = None,
    return_page: bool = False,
) -> Union[str, None]:
    """
    Method collects pages for teams.
    :param page_type: which page to parse.
    :param start: start of period.
    :param end: end of period.
    :param event: optional, key of event to restrict statistics to.
    :param match: optional, type of events to consider (collision with 'event',
                            but this is HLTV terminology).
    :param rank: optional, matches against top-X commands to consider only.
    :param data_path: optional path to html if already parsed.
    :param return_page: optional, returns page if True.
    """

    if isinstance(page_type, TeamProfile):
        link = self.get_profile_link()
    elif isinstance(page_type, TeamStat):
        link = self.get_stat_link(
            stat=page_type, start=start, end=end, match=match, event=event, rank=rank
        )
    elif str(page_type) == str(
        Ranking.TEAMS
    ):  # isinstance(page_type, Ranking) does not work !!!
        link = self.get_ranking_link(ranking=page_type, date_=end)
    else:
        raise FantasyError.invalid_arguments("page_type")

    dr = webdriver.Chrome()
    dr.get(link)

    if data_path:
        os.makedirs(os.path.dirname(data_path), exist_ok=True)
        with open(data_path, "w", encoding="utf-8") as fhandle:
            fhandle.write(dr.page_source)

    if return_page:
        return dr.page_source

    if not data_path and not return_page:
        raise FantasyError.invalid_arguments(
            "With provided 'filepath' and 'return_page', method is useless."
        )
