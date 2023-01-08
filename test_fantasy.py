import unittest
import datetime as dt
from fantasy import get_event_info, get_tournaments, EventFilter, RankFilter, Event

# Tests for 08-01-2023.


class TestFantasy(unittest.TestCase):

    def test_event_info(self):
        t1 = get_event_info(
            "https://www.hltv.org/events/6810/iem-katowice-2023-play-in")
        self.assertEqual(len(t1.players), 77)
        self.assertEqual(t1.players["11630"], "jt")
        self.assertEqual(t1.players["9102"], "sico")
        t2 = get_event_info(
            "https://www.hltv.org/events/5605/blast-premier-fall-groups-2021")
        self.assertEqual(len(t2.players), 60)
        self.assertEqual(t2.players["7998"], "s1mple")
        self.assertRaises(KeyError, t2.players.__getitem__, "19230")
        self.assertRaises(KeyError, t2.players.__getitem__, "666")
        self.assertEqual(t2.players["9766"], "hampus")
        t3 = get_event_info(
            "https://www.hltv.org/events/6586/iem-rio-major-2022")
        self.assertEqual(len(t3.players), 80)
        t4 = get_event_info(
            "https://www.hltv.org/events/6964/esl-pro-league-season-17-conference-oceania"
        )
        self.assertEqual(len(t4.players), 10)
        t5 = get_event_info(
            "https://www.hltv.org/events/6863/esl-pro-league-season-18")
        self.assertEqual(len(t5.players), 73)
        self.assertEqual(t5.players["21708"], "npl")
        self.assertRaises(KeyError, t5.players.__getitem__, "12731")

    def test_tournaments_filters(self):
        players = get_event_info(
            "https://www.hltv.org/events/6970/blast-premier-spring-groups-2023"
        ).players
        t1 = get_tournaments("13915", players["13915"], dt.date(2022, 8, 30),
                             dt.date.today(), EventFilter.ALL)
        self.assertEqual(len(t1), 6)
        t2 = get_tournaments("13915", players["13915"], dt.date(2022, 8, 30),
                             dt.date.today(), EventFilter.LAN)
        self.assertEqual(len(t2), 5)
        t3 = get_tournaments("13915", players["13915"], dt.date(2022, 8, 30),
                             dt.date.today(), EventFilter.BIG)
        self.assertEqual(len(t3), 4)
        t4 = get_tournaments("13915", players["13915"], dt.date(2022, 8, 30),
                             dt.date.today(), EventFilter.MAJORS)
        self.assertEqual(len(t4), 1)
        t5 = get_tournaments("8520", players["8520"], dt.date(2022, 3, 10),
                             dt.date.today(), EventFilter.ALL)
        self.assertEqual(len(t5), 15)
        t6 = get_tournaments("8520", players["8520"], dt.date(2022, 3, 10),
                             dt.date(2022, 11, 4), EventFilter.ALL)
        self.assertEqual(len(t6), 12)
        t7 = get_tournaments("7998", players["7998"], dt.date.today(),
                             dt.date.today(), EventFilter.LAN)
        self.assertEqual(len(t7), 0)
