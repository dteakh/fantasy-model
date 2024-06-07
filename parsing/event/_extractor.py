import os
import re
from datetime import datetime

from bs4 import Tag
from parsing.common import FantasyError, _get_src
from parsing.team import Team


def extract_main_page(self, path: str = None, src: Tag = None):
    """
    Method initializes object with main info regarding an event.
    :param path: absolute path to the event page
    :param src: page content instead of path
    """
    src = _get_src(path, src)
    self.name = src.find("h1", class_="event-hub-title").text

    if not src.find("table", class_="table eventMeta"):
        raise FantasyError.something_went_wrong(f"table not found for {path}")

    table = src.find("table", class_="table eventMeta").find_all("td")
    if len(table) != 5:
        raise FantasyError.something_went_wrong(f"too many values in table for {path}")

    self.is_qual = bool("$" != table[3].text[0])
    self.is_lan = bool("online" not in table[4].text.lower())
    self.prize_pool = (
        float(table[3].text[1:].replace(",", "")) if "$" == table[3].text[0] else 0
    )

    if table[0].text != "TBA":
        starts_at = re.sub(r"(\d+)(st|nd|rd|th)", r"\1", table[0].text)
        self.starts_at = datetime.strptime(starts_at, "%b %d %Y")

    if table[1].text != "TBA":
        ends_at = re.sub(r"(\d+)(st|nd|rd|th)", r"\1", table[1].text)
        self.ends_at = datetime.strptime(ends_at, "%b %d %Y")

    if self.starts_at and self.ends_at:
        self.duration = (self.ends_at - self.starts_at).days

    for team_box in src.find_all("div", class_="team-name"):
        for team_link in team_box.find_all("a"):
            team_attrs = team_link.get("href").split("/")

            team = Team(key=team_attrs[2], name=team_attrs[3])
            if team not in self.teams:
                self.teams.append(team)
