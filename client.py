import datetime
import pickle
import random
import select
import socket
import sqlite3

import pygame
from pygame.locals import *

from lib.functions.on_quit import save_stats
from lib.functions.start import get_maps, get_images
from lib.models.player import Player
from lib.models.screen import Screen
from lib.functions.movement import move
from lib.storage.constants import Constants
from lib.models.buttons import Button
import lib.functions.api as api

pygame.init()
pygame.font.init()
fonts = {}
for i in range(10, 25):
    fonts.update({i: pygame.font.SysFont('Comic Sans MS', i)})

SIZE = WIDTH, HEIGHT = (1920, 1080)
screen = pygame.display.set_mode(SIZE, pygame.FULLSCREEN)

HEADER = 64
PORT = 5050  # server port
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
SERVER = '192.168.1.64'  # server address to connect
BLOCK_SIZE = 32  # 60 blocks in width, 33.75 blocks in height
NOT_COLLIDING_BLOCKS = []  # blocks such as water and etc

ADDR = (SERVER, PORT)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)

db_connection = sqlite3.connect("lib/storage/database.db")
db_cur = db_connection.cursor()

db_user = db_cur.execute("SELECT * FROM user").fetchone()
print(db_user)


def send(msg):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    client.send(send_length)
    client.send(message)
    print(client.recv(2048).decode(FORMAT))


PLAYER = Player((28, 60), (100, 100), 20, 20, 1, f"Subvius-{random.randint(1, 10)}")
SCREEN = Screen()
CONSTANTS = Constants()
client.send(pickle.dumps(["id-update", PLAYER]))

running = True
clock = pygame.time.Clock()
player_id = PLAYER.nickname
players: dict[str, Player] = {}
players.update({player_id: PLAYER})

moving_left = moving_right = False

lobby_map, game_map, blocks_data = get_maps()
images, icons, mobs_images = get_images(blocks_data)

session_stats = api.get_data(CONSTANTS.api_url + f"player/?player={PLAYER.nickname}&create=True").get("stats", {})
session_stats.update({"play_time": datetime.datetime.now()})
api.post_data(CONSTANTS.api_url + f"player/?player={PLAYER.nickname}&create=True",
              {"last_login": datetime.datetime.now().timestamp(), "last_logout": 0})


def main_screen():
    on_screen = True
    buttons = [
        Button("play", 150, 25, "gray", "white", WIDTH // 2 - 75, HEIGHT // 2 - 15, "lightgray", 0),
        Button("settings", 150, 25, "gray", "white", WIDTH // 2 - 75, HEIGHT // 2 + 15, "lightgray", 1),
    ]
    title = fonts[24].render("MINECRAFT 2D MULTIPLAYER", False, "white")
    logo_title = fonts[15].render("MINECRAFT 2D", False, "white")
    while on_screen:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                exit(0)

            if event.type == MOUSEMOTION:
                pos = event.pos
                SCREEN.set_mouse_pos(pos)
                for btn in buttons:
                    btn.on_mouse_motion(*pos)

        screen.fill("black")
        background_image = images['main_screen_bg']
        logo_image = icons['logo']
        screen.blit(pygame.transform.scale(background_image, SIZE), (0, 0))

        for button in buttons:
            button.render(screen, fonts[16])

        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))
        screen.blit(pygame.transform.scale(logo_image, (128, 128)), (22, HEIGHT - 150))
        screen.blit(logo_title, (30 + 128, HEIGHT - 150 + 54))

        pygame.display.flip()
        clock.tick(60)


main_screen()

while running:
    ins, outs, ex = select.select([client], [], [], 0)

    for inm in ins:
        event = pickle.loads(inm.recv(2048))
        if event[0] == 'id-update':
            player_id = event[1]

        elif event[0] == 'players-update' and event[1] != player_id:
            players.update({event[1]: event[2]})

    if random.randint(0, 100) == 9:
        update_data = ["number!", 9]
        client.send(pickle.dumps(update_data))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
            session_stats.update({"play_time": (datetime.datetime.now() - session_stats.get("play_time")).seconds})
            save_stats(PLAYER.nickname, session_stats, CONSTANTS)
            exit(0)
        if not SCREEN.paused:
            if event.type == KEYDOWN:
                if event.key == K_LEFT:
                    moving_left = True
                elif event.key == K_RIGHT:
                    moving_right = True
                elif event.key == K_UP:
                    if PLAYER.air_timer < 6:
                        PLAYER.vertical_momentum -= 10

            if event.type == KEYUP:
                if event.key == K_LEFT:
                    moving_left = False
                elif event.key == K_RIGHT:
                    moving_right = False

    screen.fill(CONSTANTS.sky)
    colliding_objects = list()
    if SCREEN.screen == 'lobby':
        possible_x = [i for i in range(WIDTH // BLOCK_SIZE)]
        possible_y = [i for i in range(HEIGHT // BLOCK_SIZE)]
        gm_map: dict = lobby_map.get("map")

    for tile_y in possible_y:
        for tile_x in possible_x:
            block: dict = gm_map[tile_y][tile_x]
            block_id = block.get("block_id", "0")

            if block_id != "0":
                block_data = blocks_data[block_id]

                image = images[block_data["item_id"]]

                screen.blit(pygame.transform.scale(image, (BLOCK_SIZE, BLOCK_SIZE)),
                            (tile_x * BLOCK_SIZE, tile_y * BLOCK_SIZE))
                if block_id not in NOT_COLLIDING_BLOCKS:
                    block_rect = pygame.Rect(tile_x * 32, tile_y * 32, BLOCK_SIZE, BLOCK_SIZE)
                    colliding_objects.append(block_rect)

    movement = [0, 0]
    if moving_right:
        movement[0] += 2
    if moving_left:
        movement[0] -= 2
    movement[1] += PLAYER.vertical_momentum
    PLAYER.vertical_momentum = PLAYER.vertical_momentum + 0.5 if PLAYER.vertical_momentum + 0.5 <= 3 else 3

    PLAYER.rect, collisions = move(PLAYER.rect, movement, colliding_objects)
    if not collisions['bottom']:
        PLAYER.air_timer += 1
    else:
        PLAYER.air_timer = 0

    for key in players:
        player = players[key]
        pygame.draw.rect(screen, "white", player.rect)

    pygame.display.flip()

    clock.tick(60)
    if list(players.keys()).count(player_id) > 0:
        client.send(pickle.dumps(["player-update", player_id, PLAYER]))
