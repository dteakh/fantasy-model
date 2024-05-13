from datetime import date
from datetime import timedelta as td

from parsing.common import BASE, EventFilter, RankingFilter
from parsing.player._constants import PlayerStat


def get_stat_link(
    self,
    stat: PlayerStat,
    event_key: int = None,
    start_time: date = date.today() - td(weeks=12),
    end_time: date = date.today(),
    event_fil: EventFilter = EventFilter.ALL,
    ranking_fil: RankingFilter = RankingFilter.ALL,
) -> str:
    """
    Method constructs url-link of a player based on passed arguments.
    :param stat: type of statistics.
    :param event_key: key of the event.
    :param start_time: start of time period.
    :param end_time: end of time period
    :param event_fil: filter events type.
    :param ranking_fil: filter opponents.
    """

    start_time = start_time.strftime("%Y-%m-%d")
    end_time = end_time.strftime("%Y-%m-%d")
    if stat == PlayerStat.CLUTCHES:
        requested_link = (
            f"{BASE}/stats/players/{stat.value}/{self.key}/1on1/{self.name}?startDate={start_time}"
            f"&endDate={end_time}&matchType={event_fil.value}&rankingFilter={ranking_fil.value}"
        )
    else:
        requested_link = (
            f"{BASE}/stats/players/{stat.value}/{self.key}/{self.name}?startDate={start_time}"
            f"&endDate={end_time}&matchType={event_fil.value}&rankingFilter={ranking_fil.value}"
        )

    if event_key is not None:
        requested_link += f"&event={event_key}"

    return requested_link
