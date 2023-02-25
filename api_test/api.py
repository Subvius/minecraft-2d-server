import datetime
import json

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
                        "cosmetics": []
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


@app.route("/game/", methods=["GET", "POST"])
def get_game_data():
    dir_path = os.path.dirname(__file__)
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
