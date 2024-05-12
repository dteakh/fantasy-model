from common import EventFilter, RankingFilter
from team import Team, TeamStat


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

    print(profile)
    print(lineups)
    print(blast_matches)


test_team_class()
