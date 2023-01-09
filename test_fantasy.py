import unittest
import datetime as dt
from fantasy import Event, Player, FantasyError, PlayerStats, EventFilter, RankFilter

# Tests for 10-01-2023.


class TestFantasy(unittest.TestCase):

    def test_event_players(self):
        t1 = Event(6810).get_players()
        self.assertEqual(len(t1), 79)
        self.assertEqual(t1[45].key, 11630)
        self.assertEqual(t1[60], Player(key=9102, name="sico"))
        t2 = Event(5605).get_players()
        self.assertEqual(len(t2), 60)
        self.assertEqual(t2[0].key, 7998)
        self.assertFalse(Player(key=19230, name="m0nesy") in t2)
        self.assertFalse(Player(key=666, name="lavega") in t2)
        self.assertEqual(t2[27], Player(key=9766, name="hampus"))
        t3 = Event(6586).get_players()
        self.assertEqual(len(t3), 80)
        t4 = Event(6964).get_players()
        self.assertEqual(len(t4), 10)
        t5 = Event(6863).get_players()
        self.assertEqual(len(t5), 74)
        self.assertEqual(t5[34].key, 21708)
        self.assertFalse(Player(key=12731, name="sdy") in t5)

    def test_events_filter(self):
        players = Event(6970).get_players()
        t1 = players[14].get_events(dt.date(2022, 8, 30), dt.date.today(), EventFilter.ALL)
        self.assertEqual(len(t1), 6)
        t2 = players[14].get_events(dt.date(2022, 8, 30), dt.date.today(), EventFilter.LAN)
        self.assertEqual(len(t2), 5)
        t3 = players[14].get_events(dt.date(2022, 8, 30), dt.date.today(), EventFilter.BIG)
        self.assertEqual(len(t3), 4)
        t4 = players[14].get_events(dt.date(2022, 8, 30), dt.date.today(), EventFilter.MAJORS)
        self.assertEqual(len(t4), 1)
        t5 = players[11].get_events(dt.date(2022, 3, 10), dt.date.today(), EventFilter.ALL)
        self.assertEqual(len(t5), 15)
        t6 = players[11].get_events(dt.date(2022, 3, 10), dt.date(2022, 11, 4), EventFilter.ALL)
        self.assertEqual(len(t6), 12)
        t7 = players[20].get_events(dt.date.today(), dt.date.today(), EventFilter.LAN)
        self.assertEqual(len(t7), 0)

    def test_get_stats(self):
        players = Event(5728).get_players()
        st = players[3].get_event_stats(Event(6586), RankFilter.ALL)
        self.assertEqual(st[0], 1.35)
        self.assertEqual(st[-2], 81.2)
        st = players[3].get_event_stats(Event(6588), RankFilter.TOP10)
        self.assertEqual(st[3], 1.87)
        self.assertEqual(st[1], 0.53)
        with self.assertRaises(ValueError):
            players[3].get_event_stats(Event(6334), RankFilter.TOP5)
        st = players[48].get_event_stats(Event(6349), RankFilter.TOP20)
        self.assertEqual(st[0], 1.19)
        self.assertEqual(st[-2], 71.0)
        with self.assertRaises(ValueError):
            players[48].get_event_stats(Event(6349), RankFilter.TOP10)
        with self.assertRaises(ValueError):
            players[79].get_event_stats(Event(6828), RankFilter.TOP30)
        st = players[79].get_event_stats(Event(6828), RankFilter.ALL)
        self.assertEqual(st[0], 0.99)
        self.assertEqual(st[3], 0.76)
