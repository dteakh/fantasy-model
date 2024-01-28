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
