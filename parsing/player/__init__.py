from parsing.player._constants import PlayerStat


class Player:

    def __init__(self, key: int, name: str = "unknown"):
        """
        Class implements methods to parse data regarding a player.
        :param key: player's HLTV id
        :param name: player's nickname
        """

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

    from parsing.player._extractor import (
        calculate_target,
        extract_clutches_stats,
        extract_individual_stats,
        extract_matches_stats,
        extract_overview_stats,
    )
    from parsing.player._links import get_stat_link
    from parsing.player._parser import get_page
