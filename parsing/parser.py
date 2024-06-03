import gc
import json
import os
from os.path import join
from typing import List

import pandas as pd
from bs4 import BeautifulSoup, Tag
from parsing.common import (
    Config,
    EventFilter,
    RankingFilter,
    _read_path,
    get_features_name,
    get_page_name,
    get_ranking_page,
)
from parsing.event import Event
from parsing.player import PlayerStat
from parsing.team import TeamProfile, TeamStat

RANKING_PATH = join("..", "data", "rankings")


def parse_event_pages(event: Event, cfgs: List[Config], path: str, save="html"):
    """
    Parses all the data about event including teams and players.
    :param event: event object
    :param cfgs: list of filters to apply when parsing
    :param path: path to directory where event data is saved
    :param save: either "html" or "features".
    :return:
    """
    assert save in ("html", "features")
    if save == "html":
        return _parse_html(event, cfgs, path)
    elif save == "features":
        return _parse_features(event, cfgs, path)


def _parse_html(event: Event, cfgs: List[Config], path: str):
    event_dir = os.path.join(path, str(event.key))
    os.makedirs(os.path.dirname(event_dir), exist_ok=True)
    event.get_page(os.path.join(event_dir, "overview.html"))
    event.extract_main_page(os.path.join(event_dir, "overview.html"))

    teams_dir = os.path.join(event_dir, "teams")
    players_dir = os.path.join(event_dir, "players")
    os.makedirs(os.path.dirname(teams_dir), exist_ok=True)
    os.makedirs(os.path.dirname(players_dir), exist_ok=True)

    team_pages = [
        TeamStat.OVERVIEW,
        TeamStat.MATCHES,
        TeamStat.EVENT_HISTORY,
        # TeamStat.LINEUPS,   # -- already in init_lineups()
        # TeamProfile.PROFILE,  # -- deprecated, use Ranking.TEAMS instead
    ]

    player_pages = [PlayerStat.OVERVIEW, PlayerStat.CLUTCHES, PlayerStat.INDIVIDUAL]

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
                    page_type,
                    event=event.key,
                    start=cfg.start_time,
                    end=cfg.end_time,
                    match=cfg.event_fil,
                    rank=cfg.ranking_fil,
                    data_path=fpath,
                )

            for player in team.players:
                player_dir = os.path.join(players_dir, str(player.key))
                os.makedirs(os.path.dirname(player_dir), exist_ok=True)
                for page_type in player_pages:
                    fpath = os.path.join(player_dir, get_page_name(str(page_type), cfg))
                    player.get_page(
                        page_type,
                        start_time=cfg.start_time,
                        end_time=cfg.end_time,
                        event_fil=cfg.event_fil,
                        ranking_fil=cfg.ranking_fil,
                        path=fpath,
                    )

    # separate parsing of TARGET info
    # winrate for Teams, matches -> points for Players
    # single config - filtering by event only

    cfg = Config(
        start_time=event.starts_at,
        end_time=event.ends_at,
        event_fil=EventFilter.ALL,
        ranking_fil=RankingFilter.ALL,
    )
    for team in event.teams:
        team_dir = os.path.join(teams_dir, str(team.key))
        os.makedirs(os.path.dirname(team_dir), exist_ok=True)
        fpath = os.path.join(team_dir, get_page_name(str(TeamStat.MATCHES), cfg))
        team.get_page(
            TeamStat.MATCHES,
            event=event.key,
            start=cfg.start_time,
            end=cfg.end_time,
            match=cfg.event_fil,
            rank=cfg.ranking_fil,
            data_path=fpath,
        )

        for player in team.players:
            player_dir = os.path.join(players_dir, str(player.key))
            fpath = os.path.join(
                player_dir, get_page_name(str(PlayerStat.MATCHES), cfg)
            )
            player.get_page(
                PlayerStat.MATCHES,
                event_key=event.key,
                start_time=event.starts_at,
                end_time=event.ends_at,
                path=fpath,
            )


def _parse_features(event: Event, cfgs: List[Config], path: str):
    event_dir = os.path.join(path, str(event.key))
    os.makedirs(os.path.dirname(event_dir), exist_ok=True)

    if not os.path.exists(join(event_dir, "event.json")):
        with open(join(event_dir, "event.json"), "w+") as fhandle:
            json.dump(event.features_to_dict(), fhandle, indent=4, default=str)

    teams_dir = os.path.join(event_dir, "teams")
    players_dir = os.path.join(event_dir, "players")
    os.makedirs(os.path.dirname(teams_dir), exist_ok=True)
    os.makedirs(os.path.dirname(players_dir), exist_ok=True)

    team_pages = {
        "overview": TeamStat.OVERVIEW,
        "matches": TeamStat.MATCHES,
        "events": TeamStat.EVENT_HISTORY,
        "lineups": TeamStat.LINEUPS,
    }

    player_pages = {
        "overview": PlayerStat.OVERVIEW,
        "clutches": PlayerStat.CLUTCHES,
        "individual": PlayerStat.INDIVIDUAL,
    }

    for cfg in cfgs:
        features_name = get_features_name(cfg)
        print(f"Config {features_name}.")
        # TEAMS
        for team in event.teams:
            team_dir = os.path.join(teams_dir, str(team.key))

            skip_team = False
            if os.path.exists(join(team_dir, features_name)):
                skip_team = True

            ranking = get_ranking_page(cfg, rankings_path=RANKING_PATH)
            if not skip_team:
                os.makedirs(team_dir, exist_ok=True)
                # get needed HTML tags
                pages = dict()
                pages["ranking"] = _read_path(join(RANKING_PATH, ranking))
                for page_name, page_type in team_pages.items():
                    page = team.get_page(
                        page_type=page_type,
                        start=cfg.start_time,
                        end=cfg.end_time,
                        match=cfg.event_fil,
                        rank=cfg.ranking_fil,
                        return_page=True,
                    )
                    pages[page_name] = BeautifulSoup(page, "html.parser")

                # collect stats and calc features
                stats = dict()
                stats.update(
                    team.extract_ranking(
                        path=None, src=pages["ranking"], team_name=team.name
                    )
                )
                stats.update(team.extract_overview(path=None, src=pages["overview"]))
                stats.update(
                    team.extract_events(
                        path=None, src=pages["events"], match=cfg.event_fil
                    )
                )
                stats.update(team.extract_lineups(path=None, src=pages["lineups"]))
                stats.update(team.extract_matches(path=None, src=pages["matches"]))

                prep_stats = team.preprocess_stats(stats)
                features = team.get_features(prep_stats)

                # save features
                with open(
                    join(team_dir, features_name), "w", encoding="utf-8"
                ) as fhandle:
                    json.dump(features.to_dict(), fhandle, indent=4, default=str)
            elif len(team.players) == 0:
                src = _read_path(join(RANKING_PATH, ranking))
                team.init_lineups(path=None, src=src)

            # PLAYERS
            for player in team.players:
                player_dir = os.path.join(players_dir, str(player.key))
                os.makedirs(player_dir, exist_ok=True)
                if os.path.exists(join(player_dir, features_name)):
                    continue

                pages = dict()
                for page_name, page_type in player_pages.items():
                    page = player.get_page(
                        page_type,
                        start_time=cfg.start_time,
                        end_time=cfg.end_time,
                        event_fil=cfg.event_fil,
                        ranking_fil=cfg.ranking_fil,
                        return_page=True,
                    )
                    pages[page_name] = BeautifulSoup(page, "html.parser")

                # collect stats and calc features
                features = dict()
                features.update(
                    player.extract_overview_stats(path=None, src=pages["overview"])
                )
                features.update(
                    player.extract_clutches_stats(path=None, src=pages["clutches"])
                )
                features.update(
                    player.extract_individual_stats(path=None, src=pages["individual"])
                )

                # save features
                with open(
                    join(player_dir, features_name), "w+", encoding="utf-8"
                ) as fhandle:
                    json.dump(features, fhandle, indent=4, default=str)

    # need target for teams and players
    cfg = Config(
        start_time=event.starts_at,
        end_time=event.ends_at,
        event_fil=EventFilter.ALL,
        ranking_fil=RankingFilter.ALL,
    )
    target_name = "target.json"

    # TEAMS
    for team in event.teams:
        team_dir = join(teams_dir, str(team.key))
        skip_team = False
        if os.path.exists(join(team_dir, target_name)):
            skip_team = True

        if not skip_team:
            page = team.get_page(
                TeamStat.MATCHES,
                event=event.key,
                start=cfg.start_time,
                end=cfg.end_time,
                match=cfg.event_fil,
                rank=cfg.ranking_fil,
                return_page=True,
            )
            src = BeautifulSoup(page, "html.parser")
            matches = team.get_target(path=None, src=src)

            # save target
            with open(join(team_dir, target_name), "w+", encoding="utf-8") as fhandle:
                json.dump(matches, fhandle, indent=4, default=str)

        for player in team.players:
            player_dir = os.path.join(players_dir, str(player.key))
            if os.path.exists(join(player_dir, target_name)):
                continue

            page = player.get_page(
                PlayerStat.MATCHES,
                event_key=event.key,
                start_time=event.starts_at,
                end_time=event.ends_at,
                return_page=True,
            )
            src = BeautifulSoup(page, "html.parser")
            matches = player.extract_matches_stats(path=None, src=src)

            # save target
            with open(join(player_dir, target_name), "w+", encoding="utf-8") as fhandle:
                json.dump(
                    player.calculate_target(matches), fhandle, indent=4, default=str
                )
