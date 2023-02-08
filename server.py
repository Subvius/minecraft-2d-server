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


def players_update():
    for el in connections:
        player_id, con = el, connections.get(el)
        for key in players:
            player = players[key]
            if key != player_id:
                update_data = ["players-update", key, player]
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

        except pickle.UnpicklingError:
            print("неверные данные")
        except ConnectionResetError:
            print("connection reset error")
            connected = False

        except EOFError:
            print("run out of time")
            # connected = False

        except OSError:
            print("OSError")
            connected = False
    connections = {key: val for key, val in connections.items() if val != conn}
    players.pop(PLAYER_ID)
    conn.close()
    print('connection closed')


def start():
    server.listen()
    print(f"[LISTENING] Server is listening on {SERVER}")
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")


print("[STARTING] server is starting...")
start()
