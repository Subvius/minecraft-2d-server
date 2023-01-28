import datetime

from lib.functions.api import post_data
from lib.storage.constants import Constants


def save_stats(player_nickname, stats: dict, constants: Constants):
    url = constants.api_url + f"player/?player={player_nickname}&stats=True"
    post_data(url, stats)

    url = constants.api_url + f"player/?player={player_nickname}"
    data = {
        "last_logout": datetime.datetime.now().timestamp(),
    }
    post_data(url, data)
