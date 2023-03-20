"""
Update user data.
Actions only with story based fields
"""
import lib.functions.api as api
from lib.storage.constants import Constants

const = Constants()


def add_reputation(username: str, rep: int, fraction: str):
    """
    Add reputation to a user by name

    :param username: User to add reputation
    :param rep: Amount of reputation. Provide -amount to remove reputation
    :param fraction:
    :return: None
    """
    player_data = api.get_data(const.api_url + f"player/?player={username}", json_res=True).get("player")
    reputation = player_data.get("reputation", {})

    reputation.update(
        {fraction: reputation.get(fraction, 0) + rep}
    )
    api.post_data(const.api_url + "player/", {"reputation": reputation}, {"player": username})
