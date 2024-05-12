from enum import Enum


class PlayerStat(Enum):
    OVERVIEW = ""
    INDIVIDUAL = "individual"
    MATCHES = "matches"
    EVENTS = "events"
    CLUTCHES = "clutches"

    def __str__(self):
        return self.value
