from datetime import date, timedelta as td
from parsing.player._constants import PlayerStat
from parsing.common import RankingFilter, EventFilter


class Player:

    def __init__(self, key: int, name: str):
        self.key = key
        self.name = name

    def __eq__(self, other):
        if isinstance(other, Player):
            return self.key == other.key
        return False

    def __repr__(self):
        return f"{self.name} ({self.key})"

    def __str__(self):
        return f"{self.name} ({self.key})"

    from ._links import get_stat_link
    from ._stats import get_overview_stats, get_individual_stats, get_clutch_stats, get_stats
