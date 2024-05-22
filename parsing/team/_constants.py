from enum import Enum


class TeamStat(Enum):
    OVERVIEW = ""
    MATCHES = "matches"
    MAPS = "maps"
    PLAYERS = "players"
    EVENT_HISTORY = "events"
    LINEUPS = "lineups"

    def __str__(self):
        return self.value


class TeamProfile(Enum):
    PROFILE = "profile"  # for API consistency

    def __str__(self):
        return self.value


BOTTOM_WORLD_RANKING = 50
BOTTOM_RANKING_CHANGE = 0
BOTTOM_POINTS = 10
