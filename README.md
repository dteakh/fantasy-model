Everlasting HLTV Fantasy League project
--------------------------------------------
<b> NOTE: Do not browse HLTV while parsing! </b> <br />
<h2> Struct: </h1> <br />
<b> Player(key, name) </b>: <br />
<br />
-- events_link() -> link str <br />
-- stats_link() -> link str <br />
-- get_events() -> List[event id] <br />
-- get_event_stats() -> np stats vector <br />
-- get_stats_dataframe() -> df with event and stats data <br />
<br />
<b> Event(key, rank, prize, duration, isLan) </b>: <br />
<br />
-- event_info_link() -> link str <br />
-- get_players() -> List[Player] <br />
<br />
<b> fantasyalgo module (courtesy pybind11) </b>: <br />
-- best_subset(points, costs) -> best 5-subset. for n players ~ O(N choose 5) <br />
<br />


<h2> TODO: </h2> <br />
-- https://en.wikipedia.org/wiki/Hungarian_algorithm <br />
-- parse datasets <br />
-- handle df function (prep for model) <br />
-- top20 checker <br />
-- tests <br />
-- clear code <br />
:))))))))))))))))))))) <br />
<br />
<h2> Source: </h2> <br />
-- https://www.hltv.org/news/26309/introducing-fantasy <br />
-- https://www.hltv.org/fantasy
