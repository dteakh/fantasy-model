import os
from typing import List

from parsing.event import Event
from parsing.player import PlayerStat
from parsing.team import TeamProfile, TeamStat
from parsing.common import Config, get_page_name


def parse_event_pages(event: Event, cfgs: List[Config], path: str):
    """
    Parses all the data about event including teams and players.
    :param event: event object
    :param cfgs: list of filters to apply when parsing
    :param path: path to directory where event data is saved
    """

    event_dir = os.path.join(path, str(event.key))
    os.makedirs(os.path.dirname(event_dir), exist_ok=True)
    event.get_page(os.path.join(event_dir, "overview.html"))
    event.extract_main_page(os.path.join(event_dir, "overview.html"))

    teams_dir = os.path.join(event_dir, "teams")
    players_dir = os.path.join(event_dir, "players")
    os.makedirs(os.path.dirname(teams_dir), exist_ok=True)
    os.makedirs(os.path.dirname(players_dir), exist_ok=True)

    team_pages = [
        TeamStat.OVERVIEW, TeamStat.MATCHES, TeamStat.EVENT_HISTORY, TeamProfile.PROFILE
    ]

    player_pages = [
        PlayerStat.OVERVIEW, PlayerStat.CLUTCHES, PlayerStat.INDIVIDUAL, PlayerStat.MATCHES
    ]

    for team in event.teams:
        team_dir = os.path.join(teams_dir, str(team.key))
        fpath = os.path.join(team_dir, "lineup.html")
        team.get_page(TeamStat.LINEUPS, event=event.key, data_path=fpath)
        team.init_lineups(fpath)

    for cfg in cfgs:
        for team in event.teams:
            team_dir = os.path.join(teams_dir, str(team.key))
            os.makedirs(os.path.dirname(team_dir), exist_ok=True)
            for page_type in team_pages:
                fpath = os.path.join(team_dir, get_page_name(str(page_type), cfg))
                team.get_page(
                    page_type, event=event.key,
                    start=cfg.start_time, end=cfg.end_time,
                    match=cfg.event_fil, rank=cfg.ranking_fil,
                    data_path=fpath
                )

            for player in team.players:
                player_dir = os.path.join(players_dir, str(player.key))
                os.makedirs(os.path.dirname(player_dir), exist_ok=True)
                for page_type in player_pages:
                    fpath = os.path.join(player_dir, get_page_name(str(page_type), cfg))
                    player.get_page(
                        page_type, event_key=event.key,
                        start_time=cfg.start_time, end_time=cfg.end_time,
                        event_fil=cfg.event_fil, ranking_fil=cfg.ranking_fil,
                        path=fpath
                    )
