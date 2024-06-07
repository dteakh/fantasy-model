from datetime import date
from datetime import timedelta as td
from typing import Union

from parsing.common import BASE, EventFilter, Ranking, RankingFilter

from ._constants import TeamStat


def get_profile_link(self):
    """:returns: a link to team's profile on HLTV"""

    return f"{BASE}/team/{self.key}/{self.name}"


def get_stat_link(
    self,
    stat: TeamStat,
    event: int = None,
    start: date = date.today() - td(weeks=12),
    end: date = date.today(),
    match: EventFilter = EventFilter.ALL,
    rank: RankingFilter = RankingFilter.ALL,
):
    """:returns: team's statistic page URL"""

    link = f"{BASE}/stats/teams/" f"{stat}/{self.key}/{self.name}"
    if start is not None:
        link += f"?startDate={start}"
    else:
        link += f"?startDate=all"

    if end is not None:
        link += f"&endDate={end}"

    if event is not None:
        link += f"&event={event}"

    link += f"&matchType={match}&rankingFilter={rank}"
    return link


def get_ranking_link(self, ranking: Ranking, date_: date):
    """:returns: a link to world ranking at current date"""
    link = f"{BASE}/ranking/{ranking}/"
    link += f"{date_.year}/"
    link += f"{date_.strftime('%B').lower()}/"
    link += f"{date_.day}"

    return link
