import asyncio
import json
import pickle
import socket
import threading
from copy import deepcopy

from lib.models.player import Player
import config


def get_my_ip():
    """
    Find my IP address
    :return:
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()
    return ip


IP = get_my_ip()

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((IP, 8787))
server_socket.listen()

HEADER = 64
PORT = config.PORT
# SERVER = '127.0.0.1'
# SERVER = config.IPADDRESS
SERVER = IP
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)
players: dict[str, Player] = dict()
connections = dict()

with open("lib/storage/game_map.json", "r", encoding='utf-8') as f:
    game_map = json.load(f).get("map")


def players_update(nickname: str):
    for el in connections:
        player_id, con = el, connections.get(el)

        if nickname != player_id:
            update_data = ["players-update", nickname, players.get(nickname)]
            con.send(pickle.dumps(update_data))


def disconnect(player_id):
    for el in connections:
        _, con = el, connections.get(el)
        update_data = ["player-disconnect", player_id]
        con.send(pickle.dumps(update_data))


def block_id_update(pos, value):
    for el in connections:
        _, con = el, connections.get(el)
        update_data = ["block-id-update", pos, value]
        con.send(pickle.dumps(update_data))


def block_state_update(pos, field, value):
    for el in connections:
        _, con = el, connections.get(el)
        update_data = ["block-state-update", pos, field, value]
        con.send(pickle.dumps(update_data))


def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")

    connected = True
    global connections, game_map
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

                players_update(msg[1])

            elif msg[0] == 'block-break':
                print("block break")
                position = msg[1]
                game_map[position[1]][position[0]] = {"block_id": "0"}

                block_id_update(position, "0")

            elif msg[0] == 'block-placed':
                position = msg[1]
                block = msg[2]
                game_map[position[1]][position[0]].update({"block_id": block.__str__()})
                block_id_update(position, block.__str__())

            elif msg[0] == 'block-placed-background':
                position = msg[1]
                block = msg[2]
                game_map[position[1]][position[0]] = {"background_block_id": block.__str__(), "background": True}
                # map_update(position, block.__str__())

        except pickle.UnpicklingError:
            print("неверные данные")
        except ConnectionResetError:
            print("connection reset error")
            connected = False

        except EOFError:
            print("run out of time")
            connected = False

        except TypeError:
            print("Type error", addr)

        except OSError:
            print("OSError")
            connected = False

        except Exception as e:
            print(f"RAISED EXCEPTION - {e}")
    connections = {key: val for key, val in connections.items() if val != conn}
    players.pop(PLAYER_ID)
    conn.close()
    try:
        disconnect(PLAYER_ID)
    except BrokenPipeError:
        pass
    print(f"[DISCONNECT] {addr} disconnected.")
    print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 2}")


async def save_world():
    global game_map
    save = input("Save world data? Y/n\n")
    if save.lower() == "y":
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
