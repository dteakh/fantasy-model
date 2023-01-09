import unittest
import datetime as dt
from fantasy import get_event_info, get_events_links, get_stats, EventFilter, OpponentFilter, Event

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

    def test_events_filters(self):
        players = get_event_info(
            "https://www.hltv.org/events/6970/blast-premier-spring-groups-2023"
        ).players
        t1 = get_events_links("13915", players["13915"], dt.date(2022, 8, 30),
                              dt.date.today(), EventFilter.ALL)
        self.assertEqual(len(t1), 6)
        t2 = get_events_links("13915", players["13915"], dt.date(2022, 8, 30),
                              dt.date.today(), EventFilter.LAN)
        self.assertEqual(len(t2), 5)
        t3 = get_events_links("13915", players["13915"], dt.date(2022, 8, 30),
                              dt.date.today(), EventFilter.BIG)
        self.assertEqual(len(t3), 4)
        t4 = get_events_links("13915", players["13915"], dt.date(2022, 8, 30),
                              dt.date.today(), EventFilter.MAJORS)
        self.assertEqual(len(t4), 1)
        t5 = get_events_links("8520", players["8520"], dt.date(2022, 3, 10),
                              dt.date.today(), EventFilter.ALL)
        self.assertEqual(len(t5), 15)
        t6 = get_events_links("8520", players["8520"], dt.date(2022, 3, 10),
                              dt.date(2022, 11, 4), EventFilter.ALL)
        self.assertEqual(len(t6), 12)
        t7 = get_events_links("7998", players["7998"], dt.date.today(),
                              dt.date.today(), EventFilter.LAN)
        self.assertEqual(len(t7), 0)

    def test_get_stats(self):
        plrs = get_event_info(
            "https://www.hltv.org/events/5728/dreamhack-masters-spring-2021"
        ).players
        pl_id = "16920"
        events = get_events_links(pl_id, plrs[pl_id], dt.date(2022, 1, 9),
                                  dt.date.today(), EventFilter.ALL)
        event = events[0].split('=')[-1]
        st = get_stats(pl_id, plrs[pl_id], event, OpponentFilter.ALL)
        self.assertEqual(st.rating, 1.35)
        self.assertEqual(st.adr, 81.2)
        event = events[1].split('=')[-1]
        st = get_stats(pl_id, plrs[pl_id], event, OpponentFilter.TOP10)
        self.assertEqual(st.impact, 1.87)
        self.assertEqual(st.dpr, 0.53)
        event = events[-1].split('=')[-1]
        st = get_stats(pl_id, plrs[pl_id], event, OpponentFilter.TOP5)
        self.assertEqual(st, ValueError)
        pl_id = "17306"
        events = get_events_links(pl_id, plrs[pl_id], dt.date(2022, 7, 9),
                                  dt.date.today(), EventFilter.BIG)
        event = events[0].split('=')[-1]
        st = get_stats(pl_id, plrs[pl_id], event, OpponentFilter.TOP20)
        self.assertEqual(st.rating, 1.19)
        self.assertEqual(st.adr, 71.0)
        st = get_stats(pl_id, plrs[pl_id], event, OpponentFilter.TOP10)
        self.assertEqual(st, ValueError)
        pl_id = "15369"
        events = get_events_links(pl_id, plrs[pl_id], dt.date(2022, 10, 9),
                                  dt.date.today(), EventFilter.ALL)
        event = events[-1].split('=')[-1]
        st = get_stats(pl_id, plrs[pl_id], event, OpponentFilter.TOP30)
        self.assertEqual(st, ValueError)
        st = get_stats(pl_id, plrs[pl_id], event, OpponentFilter.ALL)
        self.assertEqual(st.rating, 0.99)
        self.assertEqual(st.impact, 0.76)
