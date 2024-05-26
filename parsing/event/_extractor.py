import os
import re
from datetime import datetime

from bs4 import BeautifulSoup
from parsing.common import FantasyError
from parsing.team import Team


def extract_main_page(self, path: str = None, page_data: str = None):
    """
    Method initializes object with main info regarding an event.
    :param path: absolute path to the event page
    :param page_data: page content instead of path
    """

    if not page_data:
        if not os.path.isfile(path):
            raise FantasyError.invalid_arguments(f"Not found {path}")

        with open(path, "r", encoding="utf-8") as f:
            page_data = f.read()

    src = BeautifulSoup(page_data, "html.parser")
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
            self.teams.append(Team(key=team_attrs[2], name=team_attrs[3]))
