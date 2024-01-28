from event import Event

# from team._constants import TeamStat

e = Event(6586)

teams = e.get_teams()
# print(teams[0].get_stat_link(
#             TeamStat.LINEUPS
#         ))
# print(teams[0].get_stats())
# print(teams)
print(teams[0])
stats = teams[0].get_stats()
for stat_name in stats:
    print("\n" + "-" * 20 + stat_name + "-" * 20 + "\n")
    print(stats[stat_name])
