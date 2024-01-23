from datetime import date
from common import EventFilter, RankingFilter, FantasyError, BASE


class Team:
    def __init__(self, key: int, name: str):
        self.key = key
        self.name = name

    def __eq__(self, other):
        if isinstance(other, Team):
            return self.key == other.key
        return False

    def get_events_link(self, start: str, end: str = date.today()):
        """ :returns: a link to the page with filtered events """

        return f"{BASE}/stats/teams/{self.key}?startDate={start}&endDate={end}"

    def get_stats_link(self, start: str, end: str = date.today()):
        ...




