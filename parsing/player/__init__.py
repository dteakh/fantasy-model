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

    from parsing.player._links import get_stat_link

    from parsing.player._extractor import (
        extract_overview_stats,
        extract_clutches_stats,
        extract_individual_stats,
        extract_matches_stats,
    )

    from parsing.player._parser import (
        get_overview_page,
        get_clutches_page,
        get_individual_page,
        get_matches_page,
    )
