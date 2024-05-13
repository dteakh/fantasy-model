from os.path import join
from common import EventFilter, RankingFilter
from team import Team, TeamStat
from datetime import date, timedelta as td


TEST_DATA_PATH = 'test_data'


def test_team_class():
    blast = 7552
    team = Team(4608, "NAVI")
    profile = team.get_profile_link()
    lineups = team.get_stat_link(
        stat=TeamStat.LINEUPS, match=EventFilter.ALL, rank=RankingFilter.TOP50
    )

    blast_matches = team.get_stat_link(
        stat=TeamStat.MATCHES,
        event=blast,
        match=EventFilter.ALL,
        rank=RankingFilter.TOP50,
    )

    print("\n================= LINKS =================")
    print(profile)
    print(lineups)
    print(blast_matches)

    print("\n================= RAW STATS =================")
    blast_stats = team.get_stats(event=blast, start=None, end=None)
    print(blast_stats)

    print("\n================= PREP STATS =================")
    prep_blast_stats = team.preprocess_stats(blast_stats)
    print(prep_blast_stats)

    print("\n================= RAW FEATURES =================")
    features = team.get_features(prep_blast_stats, suffix="_blast")
    # features.to_csv(join(TEST_DATA_PATH, 'features.csv'))
    print(features)


test_team_class()
