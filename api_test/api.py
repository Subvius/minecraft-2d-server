import datetime
import json

from flask import *
import os
import uuid
from data import db_session
from data.users import User
from data.guilds import Guild

app = Flask(__name__)
dir_path = os.path.dirname(__file__)

db_session.global_init("db/minecraft.db")

db_sess = db_session.create_session()


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
        user = db_sess.query(User).filter(User.nickname == player).first()

        if method == 'GET':
            try:
                if user is not None:
                    response.update({"player": user.jsonify()})
                    response.update({"success": True})
                elif create is not None and create and password is not None:
                    user = User()
                    user.nickname = player
                    user.password = password
                    user.uuid = uuid.uuid4().__str__()
                    db_sess.add(user)
                    db_sess.commit()

                    response.update({"player": user.jsonify()})
                    response.update({"success": True})
                return response
            except Exception as e:
                response.update({"E": e.__str__()})
                return response
        elif method == 'POST':
            try:
                player_update: dict = request.get_json(force=True)

                keys = list(player_update.keys())
                if stats is not None and stats:
                    for key in keys:
                        user.stats.update({
                            key: user.stats.get(key, 0) + player_update.get(key)
                        })

                elif complete_task is not None and complete_task:
                    task_id = player_update.get("id", "")
                    active_tasks = user.active_tasks
                    user.active_tasks = {key: val for key, val in active_tasks.items() if key != task_id}

                elif add_task is not None and add_task:
                    task_id = player_update.get("id")
                    user.active_tasks.update(
                        {
                            task_id: player_update
                        }
                    )
                elif update_task is not None and update_task:
                    task_id = player_update.get("id")

                    for key in keys:
                        user.active_tasks[task_id].update({
                            key: player_update.get(key)
                        })

                else:
                    for key in keys:
                        if key in list(user.jsonify().keys()):
                            exec(f"user.{key} = {player_update.get(key)}")

                db_sess.query(User).filter(User.uuid == user.uuid).update(
                    {User.active_tasks: user.active_tasks}
                )
                db_sess.commit()

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
        user = db_sess.query(User).filter(User.nickname == nickname).first()

        if password is not None and nickname is not None:

            if method == "GET":

                if create is not None:
                    if user is None:
                        user = User()
                        user.nickname = nickname
                        user.password = password
                        user.uuid = uuid.uuid4().__str__()
                        db_sess.add(user)
                        db_sess.commit()

                        response.update({"player": user.jsonify()})
                        response.update({"success": True})
                        return response

                if user is None:
                    response.update({
                        "E": "unknown user"
                    })
                    return response

                if user.password != password:
                    response.update({
                        "E": "incorrect password"
                    })
                    return response

                response.update({"player": user.jsonify()})
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
        if lb_type == "reputation":
            db_response = sorted(list(db_sess.query(User).all()), key=lambda x: sum(x.reputation.values()),
                                 reverse=True)[
                          start - 1: start - 1 + amount]

            res = [el.jsonify() for el in db_response]

        elif lb_type == 'play_time':
            db_response = sorted(list(db_sess.query(User).all()), key=lambda x: x.stats.get("play_time", 0),
                                 reverse=True)[
                          start - 1: start - 1 + amount]
            res = [el.jsonify() for el in db_response]
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


app.run(host="0.0.0.0", port=7676)
