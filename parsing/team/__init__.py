from parsing.common import Ranking
from parsing.team._constants import TeamProfile, TeamStat


class Team:
    def __init__(self, key: int, name: str):
        self.key = key
        self.name = name

        self.players = list()

    def __eq__(self, other):
        if isinstance(other, Team):
            return self.key == other.key
        return False

    def __repr__(self):
        return f"{self.name} ({self.key})"

    def __str__(self):
        return f"{self.name} ({self.key})"

    from parsing.team._extractor import (
        extract_events,  # extract_profile,
        extract_lineups,
        extract_matches,
        extract_overview,
        extract_ranking,
    )
    from parsing.team._features import get_features
    from parsing.team._links import get_profile_link, get_ranking_link, get_stat_link
    from parsing.team._parser import get_page
    from parsing.team._preprocessing import preprocess_stats


if __name__ == "__main__":
    from os.path import join

    from parsing.event import Event

    TEST_DATA_PATH = join("..", "test_data", "team")

    event_key = 7552  # blast
    event = Event(event_key)
    event.extract_main_page(join(TEST_DATA_PATH, "event_data.html"))

    team = Team(4608, "NAVI")
    team.get_page(
        page_type=Ranking.TEAMS,
        end=event.ends_at,
        data_path=join(TEST_DATA_PATH, "ranking.html"),
    )
