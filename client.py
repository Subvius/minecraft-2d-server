import datetime
import json
import pickle
import random
import select
import socket
import sqlite3
import webbrowser

import pygame
from pygame.event import Event
from pygame.locals import *

from lib.functions.npc import move_npc
from lib.functions.on_quit import save_stats
from lib.functions.start import get_maps, get_images, get_posts_surface
from lib.models.player import Player
from lib.models.screen import Screen
from lib.functions.movement import move
from lib.models.text_input import InputBox
from lib.models.touchable_opacity import TouchableOpacity
from lib.storage.constants import Constants
from lib.models.buttons import Button
import lib.functions.api as api
from lib.functions.telegram import get_recent_posts
from lib.functions.drawing import *
from lib.models.npc import Npc

pygame.init()
pygame.font.init()
fonts = {}
for i in range(10, 25):
    # fonts.update({i: pygame.font.Font(f"lib/assets/fonts/Poppins-Light.ttf", i)})
    fonts.update({i: pygame.font.SysFont("Helvetica", i)})

SIZE = WIDTH, HEIGHT = (1920, 1080)
screen = pygame.display.set_mode((1280, 787), pygame.NOFRAME)

# screen = pygame.display.set_mode(SIZE, pygame.FULLSCREEN)

HEADER = 64
PORT = 5050  # server port
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
SERVER = '192.168.1.64'  # server address to connect
BLOCK_SIZE = 32  # 60 blocks in width, 33.75 blocks in height
NOT_COLLIDING_BLOCKS = []  # blocks such as water and etc

ADDR = (SERVER, PORT)  # server address

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

db_connection = sqlite3.connect("lib/storage/database.db")
db_cur = db_connection.cursor()

db_user = db_cur.execute("SELECT * FROM user").fetchone()  # current user

get_recent_posts(contained_string="")  # get posts from telegram updates channel


def send(msg):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    client.send(send_length)
    client.send(message)
    print(client.recv(2048).decode(FORMAT))


SCREEN = Screen()
CONSTANTS = Constants()
clock = pygame.time.Clock()

moving_left = moving_right = False

lobby_map, game_map, blocks_data = get_maps()
images, icons, mobs_images = get_images(blocks_data)
session_stats = {}
PLAYER: Player = None


def log_in_screen():
    on_screen = True
    pygame.display.set_caption("Launcher - Login")
    width = 1280
    height = 787
    buttons = [
        Button("Log in", 125, 25, CONSTANTS.launch_color, "white", width // 2 - 125 // 2, height // 2 - 15,
               CONSTANTS.launch_color_hovered, 0, lighting=True),
    ]
    global screen
    login_text = fonts[18].render("Login", False, "white")
    username_input = InputBox(width // 2 - 100, 250, 200, fonts[16].get_height() + 10, fonts[16], "white", "gray",
                              False, fonts[13], True)
    password_input = InputBox(width // 2 - 100, 280, 200, fonts[16].get_height() + 10, fonts[16], "white", "gray", True,
                              fonts[13], True, min_length=8)
    input_boxes = [username_input, password_input]
    while on_screen:
        screen.fill((20, 20, 20))

        event_list = pygame.event.get()
        for event in event_list:
            if event.type == QUIT:
                pygame.quit()
                exit(0)
            for box in input_boxes:
                box.handle_event(event)
            if event.type == MOUSEMOTION:
                pos = event.pos
                SCREEN.set_mouse_pos(pos)
                for btn in buttons:
                    btn.on_mouse_motion(*pos)

            if event.type == MOUSEBUTTONDOWN:
                pos = event.pos
                btn = None
                for button in buttons:
                    res = button.on_mouse_click(*pos)
                    if res:
                        btn = button
                        break
                if btn is not None:
                    if btn.id == 0:
                        if len(username_input.text) < 5 or len(password_input.text) < 8:
                            if len(username_input.text) < 5:
                                username_input.color = (232, 101, 80)

                            if len(password_input.text) < 8:
                                password_input.color = (232, 101, 80)

                            continue
                        else:
                            global PLAYER, session_stats, db_user, db_cur, db_connection
                            PLAYER = Player((28, 60), (100, 23 * BLOCK_SIZE), 20, 20, 1,
                                            username_input.text.strip())
                            session_stats = api.get_data(
                                CONSTANTS.api_url + f"player/?player={PLAYER.nickname}&create=True&"
                                                    f"password={password_input.text}").get(
                                "stats", {})
                            session_stats.update({"play_time": datetime.datetime.now()})
                            if db_user is None:
                                db_cur.execute(
                                    f"INSERT INTO user(id, username, password, logged_in)"
                                    f" VALUES(0, '{PLAYER.nickname}',"
                                    f" '{password_input.text.strip()}', 1)")
                                db_connection.commit()
                                db_user = (
                                    0, PLAYER.nickname, password_input.text.strip(), 1
                                )

                        on_screen = False
                        pygame.display.quit()
                        pygame.display.init()
                        screen = pygame.display.set_mode(SIZE, pygame.FULLSCREEN)
                        break
                    elif btn.id == 1:
                        return start_screen()

        for btn in buttons:
            btn.render(screen, fonts[14])

        for box in input_boxes:
            box.update()
            box.draw(screen)
        screen.blit(login_text, (width // 2 - login_text.get_width() // 2, 150))

        pygame.display.flip()
        clock.tick(60)


def start_screen():
    on_screen = True
    pygame.display.set_caption("Launcher")
    width = 1280
    height = 787
    # noinspection PyTypeChecker
    buttons = [
        Button("Launch", 175, 40, CONSTANTS.launch_color_hovered, "white", width // 2 - 175 // 2, height // 2 - 150,
               CONSTANTS.launch_color, 0, lighting=True, border_radius=5),
        Button("X", 30, 32, (31, 31, 31), "white", width - 48, 18,
               (208, 53, 53), 1, lighting=True, font=fonts[16], high_light_color=(35, 35, 35), border_radius=5),

    ]
    buttons[1].toggle_high_light()
    global screen
    logo_text = fonts[18].render("Minecraft 2D Multiplayer", False, "white")
    recent_news_text = fonts[16].render("Recent News", False, "white")

    posts, posts_data = get_posts_surface(fonts, icons)
    touchables = list()
    for p_i, post in enumerate(posts):
        touchables.append(TouchableOpacity(post, (30 + 415 * p_i, 475), p_i, True))

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

                for touchable in touchables:
                    touchable.on_mouse_motion(pos)

            if event.type == MOUSEBUTTONDOWN:
                pos = event.pos
                btn = None
                for button in buttons:
                    res = button.on_mouse_click(*pos)
                    if res:
                        btn = button
                        break
                if btn is not None:
                    if btn.id == 0:
                        if db_user is None or not db_user[3]:
                            return log_in_screen()
                        else:
                            global PLAYER, session_stats
                            PLAYER = Player((28, 60), (100, 23 * BLOCK_SIZE), 20, 20, 1,
                                            db_user[1])
                            session_stats = api.get_data(
                                CONSTANTS.api_url + f"player/?player={PLAYER.nickname}&create=True&"
                                                    f"password={db_user[2]}").get(
                                "stats", {})
                            session_stats.update({"play_time": datetime.datetime.now()})
                        on_screen = False
                        pygame.display.quit()
                        pygame.display.init()
                        screen = pygame.display.set_mode(SIZE, pygame.FULLSCREEN)
                        break
                    elif btn.id == 1:
                        on_screen = False
                        pygame.quit()
                        exit(0)
                touchable = None
                for tch in touchables:
                    res = tch.on_click(pos)
                    if res:
                        touchable = tch
                        break
                if touchable is not None:
                    webbrowser.open(
                        f"https://t.me/{CONSTANTS.telegram_channel_id}/{list(posts_data.keys())[touchable.id]}")

        screen.fill((10, 10, 10))
        logo_image = icons['logo']

        screen.blit(pygame.transform.scale(images['launcher_background'], (width, 375)), (0, 68))
        for button in buttons:
            button.render(screen, fonts[20])

        screen.blit(pygame.transform.scale(logo_image, (48, 48)), (15, 15))
        screen.blit(logo_text, (85, 33))

        pygame.draw.rect(screen, (20, 19, 17), pygame.Rect(0, height // 2 + 20, width, 30))
        pygame.draw.rect(screen, (24, 24, 24), pygame.Rect(0, height // 2 + 50, width, 315))
        screen.blit(recent_news_text, (width // 2 - recent_news_text.get_width() // 2, height // 2 + 60))

        for touchable in touchables:
            touchable.render(screen)

        pygame.display.flip()
        clock.tick(60)


start_screen()

client.connect(ADDR)
client.send(pickle.dumps(["id-update", PLAYER]))

running = True
player_id = PLAYER.nickname
players: dict[str, Player] = {}
players.update({player_id: PLAYER})

api.post_data(CONSTANTS.api_url + f"player/?player={PLAYER.nickname}&create=True",
              {"last_login": datetime.datetime.now().timestamp(), "last_logout": 0})

ENTITIES_UPDATE_DELAY = 300
last_entities_update = pygame.time.get_ticks()


def main_screen():
    on_screen = True
    pygame.display.set_caption("Minecraft 2D")

    buttons = [
        Button("play", 150, 25, "gray", "white", WIDTH // 2 - 75, HEIGHT // 2 - 15, "lightgray", 0),
        Button("settings", 150, 25, "gray", "white", WIDTH // 2 - 75, HEIGHT // 2 + 15, "lightgray", 1),
        Button("", 24, 24, "gray", "white", 25, 25, "lightgray", 2),
    ]
    title = fonts[24].render("MINECRAFT 2D MULTIPLAYER", False, "white")
    logo_title = fonts[15].render("MINECRAFT 2D", False, "white")
    profile_image = icons['profile']
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

            if event.type == MOUSEBUTTONDOWN:
                pos = event.pos
                btn = None
                for button in buttons:
                    res = button.on_mouse_click(*pos)
                    if res:
                        btn = button
                        break
                if btn is not None:
                    if btn.id == 0:
                        on_screen = False
                        break
                    elif btn.id == 1:
                        pass

        screen.fill("black")
        background_image = images['main_screen_bg']
        logo_image = icons['logo']
        screen.blit(pygame.transform.scale(background_image, SIZE), (0, 0))

        for button in buttons:
            button.render(screen, fonts[16])

        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))
        screen.blit(pygame.transform.scale(logo_image, (128, 128)), (22, HEIGHT - 150))
        screen.blit(pygame.transform.scale(profile_image, (24, 24)), (25, 25))
        screen.blit(logo_title, (30 + 128, HEIGHT - 150 + 54))

        pygame.display.flip()
        clock.tick(60)


main_screen()

print(PLAYER.nickname)
sheet_path = "lib/assets/animations/Entities/player/"
PLAYER.cut_sheet(pygame.image.load(sheet_path + "idle.png"), 4, 1, "idle", 62, 80)
PLAYER.cut_sheet(pygame.image.load(sheet_path + "walk.png"), 6, 1, "walk", 50, 95)
MIRA = Npc((28, 60), (100, 23 * BLOCK_SIZE), 20, 20, 1,
           "mira", )
GREETER = Npc((28, 60), (100, 23 * BLOCK_SIZE), 20, 20, 1,
              "greeter")

npcs = [
    MIRA, GREETER
]

with open("lib/storage/story_characters.json", "r") as f:
    data: dict = json.load(f)
    for key in list(data.keys()):
        eval(f"{key.upper()}.set_coord({data[key].get('x')}, {data[key].get('y')})")
        eval(f"{key.upper()}.set_dimension('{data[key].get('dimension')}')")

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

        if event.type == KEYDOWN:
            if event.key == K_e:
                # if not SCREEN.show_dialog:
                #     SCREEN.start_dialog()
                # else:
                #     SCREEN.close_dialog()
                pass
            elif event.key == K_ESCAPE:
                if SCREEN.show_dialog:
                    SCREEN.close_dialog()
        if event.type == MOUSEMOTION:
            SCREEN.set_mouse_pos(event.pos)
        if event.type == MOUSEBUTTONDOWN:
            SCREEN.set_hold_button("left" if event.button == 1 else "right" if event.button == 3 else "middle", True)
            for npc in npcs:
                stop = npc.on_click(event.pos, event.button, SCREEN, PLAYER, (0, 0))
                if stop:
                    moving_left = moving_right = False

        if event.type == MOUSEBUTTONUP:
            SCREEN.set_hold_button("left" if event.button == 1 else "right" if event.button == 3 else "middle",
                                   False)

    current_time = pygame.time.get_ticks()
    if current_time - ENTITIES_UPDATE_DELAY > last_entities_update:
        PLAYER.update_frame()
        for npc in npcs:
            npc.update_frame()
        last_entities_update = current_time
    PLAYER.set_size(28, 60)

    screen.fill(CONSTANTS.sky)
    screen.blit(pygame.transform.scale(icons['Ocean_background_6'], SIZE), (0, 0))
    colliding_objects = list()
    if SCREEN.screen == 'lobby':
        possible_x = [i for i in range(WIDTH // BLOCK_SIZE + 2)]
        possible_y = [i for i in range(HEIGHT // BLOCK_SIZE + 1)]
        gm_map: dict = lobby_map.get("map")

    for tile_y in possible_y:
        for tile_x in possible_x:
            block: dict = gm_map[tile_y][tile_x]
            block_id = block.get("block_id", "0")

            if block_id != "0":
                block_data = blocks_data[block_id]

                image = images[block_data["item_id"]]

                screen.blit(pygame.transform.scale(image, (BLOCK_SIZE, BLOCK_SIZE)),
                            (tile_x * BLOCK_SIZE - BLOCK_SIZE, tile_y * BLOCK_SIZE))
                if block_id not in NOT_COLLIDING_BLOCKS:
                    block_rect = pygame.Rect(tile_x * BLOCK_SIZE - BLOCK_SIZE, tile_y * BLOCK_SIZE, BLOCK_SIZE,
                                             BLOCK_SIZE)
                    colliding_objects.append(block_rect)

    movement = [0, 0]
    if moving_right or moving_left:
        if PLAYER.condition != 'walk':
            PLAYER.change_condition('walk')
    else:
        if PLAYER.condition != 'idle':
            PLAYER.change_condition()
    if moving_right:
        movement[0] += 2
        PLAYER.moving_direction = 'right'
    if moving_left:
        movement[0] -= 2
        PLAYER.moving_direction = 'left'

    movement[1] += PLAYER.vertical_momentum
    PLAYER.vertical_momentum = PLAYER.vertical_momentum + 0.5 if PLAYER.vertical_momentum + 0.5 <= 3 else 3

    PLAYER.rect, collisions = move(PLAYER.rect, movement, colliding_objects)

    move_npc(npcs, colliding_objects, move)
    if not collisions['bottom']:
        PLAYER.air_timer += 1
    else:
        PLAYER.air_timer = 0

    for key in players:
        player = players[key]
        # pygame.draw.rect(screen, "white", player.rect)
        player.draw(screen, (0, 0))

    for npc in npcs:
        if SCREEN.screen == npc.dimension:
            npc.draw(screen, (0, 0))

    if SCREEN.show_dialog:
        img = pygame.transform.scale(images['dialog_window'], (WIDTH * 0.675, HEIGHT * 0.75))
        screen.blit(img,
                    (screen.get_width() // 2 - img.get_width() // 2, screen.get_height() // 2 - img.get_height() // 2))
        draw_dialog_window(screen, SCREEN, fonts[24], PLAYER)

    pygame.display.flip()

    clock.tick(60)
    if list(players.keys()).count(player_id) > 0:
        client.send(pickle.dumps(["player-update", player_id, PLAYER.server_data()]))
