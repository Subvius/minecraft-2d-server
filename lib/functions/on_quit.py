import datetime

from lib.functions.api import post_data
from lib.storage.constants import Constants


def save_stats(player_nickname, stats: dict, constants: Constants, player_stats: dict):
    for key, value in list(stats.items()):
        player_stats.update({key: player_stats.get(key) + value})
    url = constants.api_url + f"player/?player={player_nickname}&stats=True"
    post_data(url, stats)

    url = constants.api_url + f"player/?player={player_nickname}"
    data = {
        "last_logout": datetime.datetime.now().timestamp(),
    }
    post_data(url, data)
