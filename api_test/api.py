import datetime
import json

from flask import *
import os
import uuid

app = Flask(__name__)
dir_path = os.path.dirname(__file__)


@app.route('/player/', methods=["GET", "POST"])
def get_player_data():
    player = request.args.get("player")
    create = request.args.get("create")
    stats = request.args.get("stats")

    complete_task = request.args.get("complete_task")
    add_task = request.args.get("add_task")
    update_task = request.args.get("update_task")

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
                        "stats": {},
                        "cosmetics": [],
                        "reputation": {
                            "killer": 150,
                            "magician": 150,
                            "robber": 150,
                            "smuggler": 150,
                            "spice": 150
                        }
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

                elif complete_task is not None and complete_task:
                    task_id = player_update.get("id", "")
                    active_tasks = data[player].get("active_tasks", {})
                    active_tasks = {key: val for key, val in active_tasks.items() if key != task_id}

                    data[player].update({
                        "active_tasks": active_tasks
                    })
                elif add_task is not None and add_task:
                    task_id = player_update.get("id")
                    active_tasks = data[player].get("active_tasks", {})

                    active_tasks.update(
                        {
                            task_id: player_update
                        }
                    )
                    data[player].update({
                        "active_tasks": active_tasks
                    })
                elif update_task is not None and update_task:
                    task_id = player_update.get("id")
                    active_tasks = data[player].get("active_tasks", {})

                    for key in keys:
                        active_tasks[task_id].update({
                            key: player_update.get(key)
                        })

                    data[player].update({
                        "active_tasks": active_tasks
                    })

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


@app.route("/auth/", methods=["GET", "POST"])
def auth():
    method = request.method
    nickname = request.args.get("nickname")
    password = request.args.get("password")
    create = request.args.get("create")

    response = {
        "success": False
    }

    try:
        with open(os.path.join(dir_path, "players_data.json"), "r", encoding="utf-8") as f:
            json_data: dict = json.load(f)
        if password is not None and nickname is not None:

            if method == "GET":

                if create is not None:
                    if json_data.get(nickname, None) is None:
                        player_data = {
                            "id": uuid.uuid4().__str__(),
                            "password": password,
                            'nickname': nickname,
                            "first_login": datetime.datetime.now().timestamp(),
                            "last_logout": datetime.datetime.now().timestamp(),
                            "stats": {},
                            "cosmetics": [],
                            "reputation": {
                                "killer": 150,
                                "magician": 150,
                                "robber": 150,
                                "smuggler": 150,
                                "spice": 150
                            }
                        }
                        json_data.update({nickname: player_data})
                        with open(os.path.join(dir_path, 'players_data.json'), "w") as f:
                            json.dump(json_data, f)

                        response.update({"player": player_data})
                        response.update({"success": True})

                if json_data.get(nickname, None) is None:
                    response.update({
                        "E": "unknown user"
                    })
                    return response

                if json_data.get(nickname).get("password") != password:
                    response.update({
                        "E": "incorrect password"
                    })
                    return response

                response.update({"player": json_data.get(nickname)})
                response.update({"success": True})
                return response

        else:
            response.update({
                "E": "Not enough arguments. Usage: nickname=Nickname&password=Password."
            })
            return response

    except Exception as e:
        response.update({"E": e.__str__()})

    return response


@app.route("/leaderboard/", methods=["GET"])
def get_leaderboard():
    lb_type = request.args.get("type", "reputation")
    start = request.args.get("start", 1)
    amount = request.args.get("amount", 10)

    response = {
        "success": False
    }

    try:
        start, amount = int(start), int(amount)
        with open(os.path.join(dir_path, "players_data.json"), "r") as f:
            data: dict = json.load(f)
        if lb_type == "reputation":

            res = [el for el in
                   sorted(
                       list(data.values()),
                       key=lambda x: sum([rep for rep in x.get("reputation", {}).values()]),
                       reverse=True
                   )[start - 1: start - 1 + amount]]
        elif lb_type == 'play_time':
            res = [el for el in
                   sorted(
                       list(data.values()),
                       key=lambda x: x.get("stats", {}).get("play_time", 0),
                       reverse=True
                   )[start - 1: start - 1 + amount]]
        else:
            res = []

        response.update(
            {
                "data": res,
                "success": True
            }
        )
        return response

    except Exception as e:
        response.update({"E": e.__str__()})

    return response


@app.route("/announcement/", methods=["GET", "POST"])
def announcement():
    method = request.method
    create = request.args.get("create")
    update = request.args.get("update")
    delete = request.args.get("delete")

    response = {
        "success": False
    }
    try:
        with open(os.path.join(dir_path, "game_data.json"), "r") as f:
            game_data: dict = json.load(f)

        if method == "GET":
            response.update({
                "success": True,
                "data": game_data
            })
            return response

        elif method == "POST":
            request_data = request.get_json(force=True)

            if create is not None:
                game_data.update({
                    "announcement": {
                        "text": request_data.get("text"),
                        "end": request_data.get("end"),
                    }
                })
            elif update is not None:
                for key, value in list(request_data.items()):
                    game_data.update({
                        "announcement": {
                            key: value,
                        }
                    })
            elif delete is not None:
                game_data.update({
                    "announcement": None
                })

            with open(os.path.join(dir_path, "game_data.json"), "w") as f:
                json.dump(game_data, f)

            response.update({"success": True})
            return response

    except Exception as e:
        response.update({"E": e.__str__()})
        return response
    return response


@app.route("/game/", methods=["GET", "POST"])
def get_game_data():
    method = request.method
    update = request.args.get("update")

    response = {
        "success": False
    }
    try:
        with open(os.path.join(dir_path, "manifest.json"), "r") as f:
            manifest: dict = json.load(f)

        if method == "GET":
            response.update({
                "game": manifest,
                "success": True
            })
            return response

        elif method == "POST":
            update_data = request.get_json(force=True)
            if update is not None:

                for key, value in list(update_data.items()):
                    if key not in ["version", "build_number"]:
                        manifest.update({
                            key: value
                        })
                    else:
                        manifest.update({
                            key: manifest.get(key) + value
                        })

                with open(os.path.join(dir_path, "manifest.json"), "w") as f:
                    json.dump(manifest, f)

                response.update({
                    "success": True
                })

            return response

    except Exception as e:
        response.update({"E": e.__str__()})
        return response
    return response
