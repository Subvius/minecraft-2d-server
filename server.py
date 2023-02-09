import asyncio
import json
import pickle
import socket
import threading
from lib.models.player import Player

HEADER = 64
PORT = 5050
# SERVER = '127.0.0.1'
SERVER = '192.168.1.64'
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)
players: dict[str, Player] = dict()
connections = dict()

with open("lib/storage/game_map.json", "r", encoding='utf-8') as f:
    game_map = json.load(f).get("map")


def players_update():
    for el in connections:
        player_id, con = el, connections.get(el)
        for key in players:
            player = players[key]
            if key != player_id:
                update_data = ["players-update", key, player]
                con.send(pickle.dumps(update_data))


def disconnect(player_id):
    for el in connections:
        _, con = el, connections.get(el)
        update_data = ["player-disconnect", player_id]
        con.send(pickle.dumps(update_data))


def map_update(pos, value):
    for el in connections:
        _, con = el, connections.get(el)
        update_data = ["block-update", pos, value]
        con.send(pickle.dumps(update_data))


def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")

    connected = True
    global connections
    PLAYER_ID = ""
    while connected:
        try:
            msg = pickle.loads(conn.recv(4096))
            if msg == DISCONNECT_MESSAGE:
                connected = False

            elif msg[0] == 'id-update':
                player = msg[1]
                connections.update({player.nickname: conn})
                players[player.nickname] = player
                PLAYER_ID = player.nickname
                players_update()

            elif msg[0] == "player-update":
                players[msg[1]] = msg[2]

                players_update()

            elif msg[0] == 'block-break':
                position = msg[1]
                game_map[position[1]][position[0]] = {"block_id": "0"}

                map_update(position, game_map[position[1]][position[0]])

        except pickle.UnpicklingError:
            print("неверные данные")
        except ConnectionResetError:
            print("connection reset error")
            connected = False

        except EOFError:
            print("run out of time")
            connected = False

        except OSError:
            print("OSError")
            connected = False
    connections = {key: val for key, val in connections.items() if val != conn}
    players.pop(PLAYER_ID)
    conn.close()
    disconnect(PLAYER_ID)
    print(f"[DISCONNECT] {addr} disconnected.")
    print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 2}")


async def save_world():
    print("[SAVE] saving world data...")
    with open("lib/storage/game_map.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    data.update({"map": game_map})

    with open("lib/storage/game_map.json", "w") as f:
        json.dump(data, f)

    print("[SAVE] world data has been saved.")


async def on_shutdown():
    tasks = [
        asyncio.create_task(save_world())
    ]
    await asyncio.gather(*tasks)


def start():
    server.listen()
    print(f"[LISTENING] Server is listening on {SERVER}")
    while True:
        try:
            conn, addr = server.accept()
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            thread.start()
            print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")
        except KeyboardInterrupt:
            return


print("[STARTING] server is starting...")
start()
print("[SHUTDOWN] server is shutting down...")
asyncio.run(on_shutdown())
print("[SHUTDOWN] server has shut down.")
