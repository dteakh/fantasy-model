import os
import json
from os.path import join, basename
from typing import List, Tuple

import numpy as np
import pandas as pd

from parsing.common import unstack_features_name
from parsing.team._utils import get_winrate
from sklearn.base import TransformerMixin
from sklearn.preprocessing import OneHotEncoder, StandardScaler


def _read_json(path: str, df=True, single_row=False, **kwargs) -> pd.DataFrame:
    if df:
        try:
            df = pd.read_json(path, **kwargs)
            return df
        except:
            pass

    with open(path, "r+") as fhandle:
        content = json.load(fhandle)

    if df:
        if single_row:
            return pd.DataFrame(content, index=[0])
        else:
            return pd.DataFrame(content, index=list(range(len(content))))
    else:
        return content


def get_event_dataset(event_dir: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
    assert os.path.exists(event_dir), f"Provided path '{event_dir}' does not exist."

    event_df = _read_json(join(event_dir, "event.json"), single_row=True)
    event_df["event_id"] = int(basename(event_dir))
    team2player = _read_json(join(event_dir, "team2player.json"), df=False)
    player2team = _read_json(join(event_dir, "player2team.json"), df=False)
    team_id2name = _read_json(join(event_dir, "team_id2name.json"), df=False)
    player_id2name = _read_json(join(event_dir, "player_id2name.json"), df=False)

    teams = []
    teams_dir = join(event_dir, "teams")

    for team_id in os.listdir(teams_dir):
        if not team_id.isdigit():  # local OS files
            continue

        team_dir = join(teams_dir, team_id)
        features_names = os.listdir(team_dir)
        features_names = [fn for fn in features_names if (len(fn.split("_")) == 4)]

        team_dfs = []
        for fn in features_names:
            team_df = _read_json(join(team_dir, fn))
            cfg = unstack_features_name(fn)
            for k, v in cfg.items():
                team_df[k] = v

            team_dfs.append(team_df)

        team_df = pd.concat(team_dfs, axis=0, ignore_index=True).reset_index(drop=True)
        for i in range(5):
            team_df[f"player_id_{i + 1}"] = team2player[team_id][i]

        with open(join(team_dir, "target.json"), "r") as fhandle:
            matches = json.load(fhandle)

        wr = get_winrate(matches)
        team_df["wr_target"] = wr
        team_df["team_id"] = int(team_id)
        team_df["team_name"] = team_id2name[team_id]

        teams.append(team_df)

    teams_df = pd.concat(teams, axis=0, ignore_index=True).reset_index(drop=True)

    players = []
    players_dir = join(event_dir, "players")

    for player_id in os.listdir(players_dir):
        if not player_id.isdigit():
            continue

        player_dir = join(players_dir, player_id)
        features_names = os.listdir(player_dir)
        features_names = [fn for fn in features_names if (len(fn.split("_")) == 4)]

        player_dfs = []
        for fn in features_names:
            player_df = _read_json(join(player_dir, fn))
            cfg = unstack_features_name(fn)
            for k, v in cfg.items():
                player_df[k] = v

            player_dfs.append(player_df)

        player_df = pd.concat(player_dfs, axis=0, ignore_index=True).reset_index(drop=True)
        try:  # TODO: при последующем парсинге, такой ошибки быть не может. LEGACY.
            player_df["team_id"] = int(player2team[player_id])
            player_df["player_name"] = player_id2name[player_id]
        except:
            print(f"Player with id={player_id} has no matching team_id.")
            player_df["team_id"] = None
            player_df["player_name"] = None

        with open(join(player_dir, "target.json"), "r") as fhandle:
            expected_pts = fhandle.read()

        player_df["expected_pts_target"] = float(expected_pts)
        player_df["player_id"] = int(player_id)

        players.append(player_df)

    players_df = pd.concat(players, axis=0, ignore_index=True).reset_index(drop=True)

    assert len(event_df) == 1, "Event dataframe has multiple rows."

    for col in event_df.columns:
        teams_df[col] = event_df.loc[0, col]
        players_df[col] = event_df.loc[0, col]

    return teams_df, players_df


def get_dataset(event_dirs: List[str]):
    teams, players = [], []
    for event_dir in event_dirs:
        teams_df, players_df = get_event_dataset(event_dir)
        teams.append(teams_df)
        players.append(players_df)

    teams = pd.concat(teams, axis=0, ignore_index=True).reset_index(drop=True)
    players = pd.concat(players, axis=0, ignore_index=True).reset_index(drop=True)

    return teams, players


def get_target(pts: float, wr: float) -> float:
    return pts + 9 * wr - 3


class Preprocessor(TransformerMixin):
    def __init__(self, cat_cols, bin_cols):
        self.onehot = OneHotEncoder(sparse_output=False)
        self.scaler = StandardScaler()
        self.cat_cols = cat_cols
        self.bin_cols = bin_cols
        self.features: np.array = None

    def _get_rest_cols(self, cols):
        return [c for c in cols if c not in self.bin_cols + self.cat_cols]

    def fit(self, X, y=None):
        self.scaler.fit(X[self._get_rest_cols(X.columns)])
        self.onehot.fit(X[self.cat_cols])

        self.features = np.hstack([
            self._get_rest_cols(X.columns),
            self.onehot.get_feature_names_out(),
            self.bin_cols
        ]).reshape(1, -1)
        return self

    def transform(self, X, y=None):
        assert isinstance(X, pd.DataFrame), "Dataframe must be passed to infer categorical columns."

        index = X.index
        X_sc = self.scaler.transform(X[self._get_rest_cols(X.columns)])
        X_sc = pd.DataFrame(X_sc, index=index, columns=self._get_rest_cols(X.columns))
        res = X_sc.join(X[self.bin_cols])

        X_cat = self.onehot.transform(X[self.cat_cols])
        X_cat = pd.DataFrame(data=X_cat, columns=self.onehot.get_feature_names_out())
        X_cat = X_cat.set_index(index, drop=True)

        res = res.join(X_cat)
        assert set(res.columns.values.tolist()) == set(self.features.tolist()[0])
        return res[self.features.tolist()[0]].reset_index(drop=True).astype(np.float64)
