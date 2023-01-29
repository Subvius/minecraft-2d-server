import datetime

from flask import *
import os
import uuid

app = Flask(__name__)


@app.route('/player/', methods=["GET", "POST"])
def get_player_data():
    dir_path = os.path.dirname(__file__)
    player = request.args.get("player")
    create = request.args.get("create")
    stats = request.args.get("stats")
    password = request.args.get("password")
    method = request.method
    response = {
        "success": False,
    }
    if player is not None:
        if method == 'GET':
            try:
                with open(os.path.join(dir_path, 'players_data.json'), "r") as f:
                    data = json.load(f)
                player_data = data.get(player, None)
                if player_data is not None:
                    response.update({"player": player_data})
                    response.update({"success": True})
                elif create is not None and create and password is not None:
                    player_data = {
                        "id": uuid.uuid4().__str__(),
                        "password": password,
                        'nickname': player,
                        "first_login": datetime.datetime.now().timestamp(),
                        "last_logout": datetime.datetime.now().timestamp(),
                        "stats": {}
                    }
                    data.update({player: player_data})
                    with open(os.path.join(dir_path, 'players_data.json'), "w") as f:
                        json.dump(data, f)

                    response.update({"player": player_data})
                    response.update({"success": True})
                return response
            except Exception as e:
                response.update({"E": e.__str__()})
                return response
        elif method == 'POST':
            try:
                with open(os.path.join(dir_path, 'players_data.json'), "r") as f:
                    data = json.load(f)
                player_update: dict = request.get_json(force=True)
                if player not in list(data.keys()):
                    data.update({player: {}})

                keys = list(player_update.keys())
                if stats is not None and stats:
                    for key in keys:
                        data[player]['stats'].update({key: data[player]['stats'].get(key, 0) + player_update.get(key)})
                else:
                    for key in keys:
                        data[player].update({key: player_update.get(key)})
                with open(os.path.join(dir_path, 'players_data.json'), "w") as f:
                    json.dump(data, f)
                response.update({"success": True})
                return response
            except Exception as e:
                print(e)
                response.update({"E": e.__str__()})
                return response

    return response
