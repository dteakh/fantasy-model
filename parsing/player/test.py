from parsing.player import Player
from datetime import date, timedelta as td

if __name__ == '__main__':
    player = Player(key=21167, name='donk')
    data = player.get_stats(start_time=date.today() - td(weeks=50), end_time=date.today())
    print(data)