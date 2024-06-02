from typing import List
from parsing.team import Team
from bs4 import BeautifulSoup


class Event:

    def __init__(self, key: int):
        """
        Class implements methods to parse data regarding an event.
        :param key: event's HLTV id
        """

        self.key = key
        self.name = None

        self.is_lan = None
        self.is_qual = None
        self.prize_pool = None

        self.starts_at = None
        self.ends_at = None
        self.duration = None

        self.teams: List[Team] = []

        page_data = self.get_page(return_page=True)
        src = BeautifulSoup(page_data, "html.parser")
        self.extract_main_page(path=None, src=src)

    def features_to_dict(self):
        return {
            "is_lan": self.is_lan,
            "is_qual": self.is_qual,
            "prize_pool": self.prize_pool,
            "start_at": self.starts_at,
            "ends_at": self.ends_at,
            "duration": self.duration,
        }

    def __eq__(self, other):
        if isinstance(other, Event):
            return self.key == other.key
        return False

    def __repr__(self):
        return f"{self.name} ({self.key})"

    def __str__(self):
        return f"{self.name} ({self.key})"

    from parsing.event._extractor import extract_main_page
    from parsing.event._links import get_event_link
    from parsing.event._parser import get_page
