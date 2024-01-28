from datetime import date
from datetime import timedelta as td
from typing import Union

from parsing.common import BASE, EventFilter, RankingFilter

from ._constants import TeamStat


def get_profile_link(self):
    """:returns: a link to team's profile on HLTV"""

    return f"{BASE}/team/{self.key}/{self.name}"


def get_stat_link(
    self,
    stat: TeamStat,
    event: int = None,
    start: Union[str, date] = date.today() - td(weeks=12),
    end: Union[str, date] = date.today(),
    match: EventFilter = EventFilter.ALL,
    rank: RankingFilter = RankingFilter.ALL,
):
    """:returns: get team's statistic page URL"""

    link = (
        f"{BASE}/stats/teams/"
        f"{stat}/{self.key}/{self.name}"
        f"?startDate={start}&endDate={end}"
    )

    if event is not None:
        link += f"&event={event}"

    link += f"&matchType={match}&rankingFilter={rank}"
    return link
