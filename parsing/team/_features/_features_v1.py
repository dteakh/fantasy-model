import numpy as np
import pandas as pd

from typing import Dict, List, Union

from parsing.team._utils import _get_placement, _get_intensity


def get_features(
        self,
        prep_stats: Dict[str, Union[Dict[str, str], List[Dict[str, str]]]],
        suffix: str = None
) -> pd.DataFrame:
    """
    Method calculates team features for preprocessed stats.
    :param self:
    :param prep_stats: preprocessed stats.
    :param suffix: suffix to append to all features.
    :return: pandas DataFrame with features.
    """
    features = dict()

    features["has_roster_change"] = (len(prep_stats["lineups"]) > 1)
    features["world_ranking"] = prep_stats["profile"]["world_ranking"]
    features["weeks_in_top30_core"] = prep_stats["profile"]["weeks_in_top30_core"]

    events = prep_stats["events"]
    plcmnts = [_get_placement(e["placement"]) for e in events]
    features[f"avg_place"] = sum(plcmnts) / len(plcmnts) if len(plcmnts) > 0 else np.nan

    mtchs = prep_stats["matches"]
    features[f"winrate"] = sum(m["is_winner"] for m in mtchs) / max(1, len(mtchs))

    features[f"avg_match_intensity"] = sum([_get_intensity(m) for m in mtchs]) / max(1, len(mtchs))

    wins = [m for m in mtchs if m["is_winner"]]
    features[f"avg_win_intensity"] = sum([_get_intensity(w) for w in wins]) / max(1, len(wins))

    losses = [m for m in mtchs if not m["is_winner"]]
    features[f"avg_loss_intensity"] = sum([_get_intensity(l) for l in losses]) / max(1, len(losses))

    winstreak = 0
    for m in mtchs:  # sorted by time already
        if not m["is_winner"]:
            break
        winstreak += 1

    features[f"winstreak"] = winstreak

    features[f"matches_played"] = len(mtchs)

    features = pd.DataFrame(features, index=[0])

    if suffix is not None:
        features = features.add_suffix(suffix=suffix, axis=1)

    return features
