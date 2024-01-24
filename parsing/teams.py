from datetime import date, timedelta as td
from enum import Enum
from typing import Union

import pandas as pd
from selenium import webdriver
from common import (
    EventFilter,
    RankingFilter,
    set_timeout,
    FantasyError,
    BASE,
    TIMEOUT
)


class TeamStat(Enum):
    OVERVIEW = ""
    MATCHES = "matches"
    MAPS = "maps"
    PLAYERS = "players"
    EVENT_HISTORY = "events"
    LINEUPS = "lineups"

    def __str__(self):
        return self.value


class Team:
    def __init__(self, key: int, name: str):
        self.key = key
        self.name = name

    def __eq__(self, other):
        if isinstance(other, Team):
            return self.key == other.key
        return False

    def get_profile_link(self):
        """ :returns: a link to team's profile on HLTV """

        return f"{BASE}/team/{self.key}/{self.name}"

    def get_stat(
            self,
            stat: TeamStat,
            event: int = None,
            start: Union[str, date] = date.today() - td(weeks=12),
            end: Union[str, date] = date.today(),
            match: EventFilter = EventFilter.ALL,
            rank: RankingFilter = RankingFilter.ALL
    ):
        """ :returns: get team's statistic page """

        link = f"{BASE}/stats/teams/" \
               f"{stat}/{self.key}/{self.name}" \
               f"?startDate={start}&endDate={end}"

        if event is not None:
            link += f"&event={event}"

        link += f"&matchType={match}&rankingFilter={rank}"
        return link

    @set_timeout(TIMEOUT)
    def parse_hltv(self, start: date, end: date, delta: td) -> Union[pd.DataFrame, None]:
        ...

    def get_features(self, parsed_data: pd.DataFrame) -> Union[pd.DataFrame, None]:
        ...


if __name__ == "__main__":
    def test_team_class():
        blast = 7552
        team = Team(4608, "NAVI")
        profile = team.get_profile_link()
        lineups = team.get_stat(
            stat=TeamStat.LINEUPS,
            match=EventFilter.ALL,
            rank=RankingFilter.TOP50)

        blast_matches = team.get_stat(
            stat=TeamStat.MATCHES,
            event=blast,
            match=EventFilter.ALL,
            rank=RankingFilter.TOP50)

        print(profile)
        print(lineups)
        print(blast_matches)


    test_team_class()

