from parsing.common import BASE


def get_event_link(self) -> str:
    return f"{BASE}/events/{self.key}/event"
