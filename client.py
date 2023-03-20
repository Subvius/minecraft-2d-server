import asyncio
import datetime
import math
import os
import pickle
import random
import select
import shutil
import socket
import sqlite3
import sys
import webbrowser
from copy import deepcopy

import pygame.image

import config

from pygame.locals import *

from lib.functions.blocks import get_block_from_coords
from lib.functions.map_actions import is_close, on_left_click, on_right_click
from lib.functions.npc import move_npc
from lib.functions.on_quit import save_stats
from lib.functions.run_multiple_tasks import run_multiple_tasks
from lib.functions.start import get_maps, get_images, get_posts_surface, load_player_images
from lib.models.notifications import Notification
from lib.models.player import Player
from lib.functions.movement import move
from lib.models.storytasks import StoryTasks
from lib.models.text_input import InputBox
from lib.models.touchable_opacity import TouchableOpacity
from lib.storage.constants import Constants
from lib.models.buttons import Button
import lib.functions.api as api
from lib.functions.telegram import get_recent_posts
from lib.models.screen import *

from lib.functions.drawing import draw_rect_alpha, draw_dialog_window, draw_inventory, draw_rep, draw_tasks
from lib.models.npc import Npc

from lib.users.skin.generate_animations import generate_animations, generate_preview

if os.path.exists("lib/temp/session/"):
    shutil.rmtree("lib/temp/session/")
os.mkdir("lib/temp/session/")

pygame.init()
pygame.font.init()
fonts = {}
for i in range(10, 25):
    # fonts.update({i: pygame.font.Font(f"lib/assets/fonts/Poppins-Light.ttf", i)})
    fonts.update({i: pygame.font.SysFont("Helvetica", i)})

SIZE = WIDTH, HEIGHT = config.WINDOW_SIZE
screen = pygame.display.set_mode((1280, 787), pygame.NOFRAME)

# screen = pygame.display.set_mode(SIZE, pygame.FULLSCREEN)

HEADER = 64
PORT = config.PORT  # server port
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
SERVER = config.IPADDRESS  # server address to connect
BLOCK_SIZE = 32  # 42.5 blocks in width, 24 blocks in height
NOT_COLLIDING_BLOCKS = []  # blocks such as water and etc
FRACTIONS = ["killer", "magician", "smuggler"]  # Story fractions of npcs and da player
CASTLE_AREA = ((7744, 1952), (9856, 1952))

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

moving_left = moving_right = jumping = False

lobby_map, game_map, blocks_data = get_maps()
images, icons, mobs_images, block_breaking, cloaks_images = get_images(blocks_data)
session_stats = dict()
player_stats = dict()
PLAYER: Player = None
PLAYER_DATA = dict()
STORY_WORLD_COORD = (0, 0)


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
    notification = Notification("", 3, (width, height),
                                notification_type="danger")
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
                            res = api.get_data(
                                CONSTANTS.api_url + f"auth/?nickname={username_input.text.strip()}&"
                                                    f"password={password_input.text}&create=True")
                            if res.get("success", False):
                                global PLAYER, session_stats, db_user, db_cur, db_connection, player_stats
                                PLAYER = Player((28, 60), (100, 12 * BLOCK_SIZE), 20, 20, 1,
                                                username_input.text.strip())
                                api_data = res.get("player")

                                global STORY_WORLD_COORD, PLAYER_DATA
                                PLAYER_DATA = api_data
                                if api_data.get("story_world_coord", None) is None:
                                    STORY_WORLD_COORD = (1240, 2340)
                                else:
                                    STORY_WORLD_COORD = api_data.get("story_world_coord")
                                player_stats = api_data.get(
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
                            else:
                                error = res.get("E")
                                if error.count("password"):
                                    password_input.color = (232, 101, 80)
                                    notification.set_text("Incorrect password.")
                                    notification.set_type("danger")
                                    notification.show_window()
                                elif error.count("unknown"):
                                    username_input.color = (232, 101, 80)
                                    notification.set_text("Unknown user.")
                                    notification.set_type("danger")
                                    notification.show_window()
                                continue

                        try:
                            client.connect(ADDR)
                        except Exception as _:
                            notification = Notification("Unable to connect to the server. Try again later.", 4,
                                                        (width, height),
                                                        notification_type="danger")
                            notification.show_window()
                            continue
                        on_screen = False
                        pygame.display.quit()
                        pygame.display.init()
                        screen = pygame.display.set_mode(SIZE
                                                         # , pygame.FULLSCREEN
                                                         )
                        break
                    elif btn.id == 1:
                        return start_screen()

        for btn in buttons:
            btn.render(screen, fonts[14])

        for box in input_boxes:
            box.update()
            box.draw(screen)
        screen.blit(login_text, (width // 2 - login_text.get_width() // 2, 150))

        notification.draw(screen, None)
        pygame.display.flip()
        clock.tick(60)


async def fetch_skins(skin_uuid, nickname, cloak, ignore_existing_file=False):
    if skin_uuid is None:
        skin_uuid = api.get_data(f"https://minecraft-api.com/api/uuid/{nickname}",
                                 json_res=False).content.decode(encoding="utf-8")
        PLAYER_DATA.update({"skin_uuid": skin_uuid})
    if not skin_uuid.lower().count("player"):
        if os.path.exists("lib/temp/session/front_image.png") and not ignore_existing_file:
            skin_image = pygame.image.load("lib/temp/session/front_image.png")
            cloak_preview = pygame.image.load("lib/temp/session/cloak_preview.png")
        else:
            res = api.get_data(f"https://mineskin.eu/skin/{skin_uuid}", json_res=False)
            shutil.copyfile(f"lib/users/skin/raw_steve.png", f"lib/temp/raw_skins/{nickname}.png")
            with open(f"lib/temp/raw_skins/{nickname}.png", "wb") as f:
                f.write(res.content)

            await generate_preview(f"lib/temp/raw_skins/{nickname}.png", "lib/temp/session/", cloak)

            skin_image = pygame.image.load("lib/temp/session/front_image.png")
            cloak_preview = pygame.image.load("lib/temp/session/cloak_preview.png")

    else:
        skin_image = pygame.image.load("lib/users/skin/front_body_steve.png")
        cloak_preview = pygame.image.load("lib/users/skin/front_body_steve.png")

    return skin_image, cloak_preview


def customise_character():
    on_screen = True
    pygame.display.set_caption("Launcher - Customise Character")
    width = 1280
    height = 787
    buttons = [
        Button("X", 30, 32, (31, 31, 31), "white", width - 48, 18,
               (208, 53, 53), 0, lighting=True, font=fonts[16], high_light_color=(35, 35, 35), border_radius=5),
        Button("Home", 50, 32, (10, 10, 10), "white", 380, 30,
               (31, 31, 31), 1, font=fonts[14], high_light_color=(35, 35, 35), border_radius=5, ),
        Button("Skin", 50, 32, (31, 31, 31), "white", 450, 30,
               (31, 31, 31), 2, font=fonts[14], high_light_color=(35, 35, 35), border_radius=5, ),
        Button("Show cloak", 200, 32, "#10acf4", "white", 420, 168,
               "#107bf4", 3, font=fonts[14], high_light_color=(35, 35, 35), border_radius=5, ),
        Button("Save changes", 200, 32, "#12d016", "white", 420, 340,
               "#15bf31", 4, font=fonts[14], high_light_color=(35, 35, 35), border_radius=5, ),

    ]
    buttons[0].toggle_high_light()
    buttons[2].toggle_high_light()

    global screen, PLAYER, PLAYER_DATA

    logo_text = fonts[18].render("Minecraft 2D Multiplayer", False, "white")
    skin_uuid = PLAYER_DATA.get("skin_uuid", None)
    selected_cloak = PLAYER_DATA.get("cloak", None)
    skin_image, cloak_preview = asyncio.run(fetch_skins(skin_uuid, PLAYER.nickname, selected_cloak))
    show_cloak = False
    cosmetics = PLAYER_DATA.get("cosmetics", None)

    current_skin_name = api.get_data(
        f"https://minecraft-api.com/api/pseudo/{skin_uuid}/json").get(
        "pseudo") if skin_uuid is not None and not skin_uuid.lower().count('player') else PLAYER.nickname

    skin_name_input = InputBox(420, 125, 200, fonts[16].get_height() + 10, fonts[16], "white", "gray",
                               False, fonts[13], False, text=current_skin_name)
    last_input = datetime.datetime.now()
    fetched = True
    input_boxes = [skin_name_input, ]

    touchables = list()
    _cosmetic_names = dict()
    notification = Notification("Changes have been saved.", 2, (width, height), )

    if cosmetics is not None:
        prev_height = 0
        for index, value in enumerate(list(cosmetics.values())):
            y = 105 + prev_height + 15
            x = 840

            for ci, cloak in enumerate(value):
                cx = x + (ci % 3) * 56
                cy = y + (ci // 3) * 100

                touchables.append(
                    TouchableOpacity(pygame.transform.smoothscale(cloaks_images.get(cloak), (48, 96)), (cx, cy),
                                     ci + index * 3, )
                )
                _cosmetic_names.update({
                    ci + index * 3: cloak
                })

    while on_screen:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                exit(0)
            for box in input_boxes:
                box.handle_event(event)

            if event.type == KEYDOWN:
                last_input = datetime.datetime.now()
                fetched = False
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
                        on_screen = False
                        pygame.quit()
                        exit(0)
                    elif btn.id == 1:
                        on_screen = False
                        return start_screen()
                    elif btn.id == 3:
                        show_cloak = not show_cloak
                        buttons[3].label = "Show cloak" if not show_cloak else "Show skin"

                    elif btn.id == 4:
                        update_data = {
                            "skin_uuid": skin_uuid,
                            "cloak": selected_cloak
                        }
                        PLAYER_DATA.update(
                            update_data
                        )

                        res = api.post_data(CONSTANTS.api_url + f"player/?player={PLAYER.nickname}", update_data)
                        if res.get("success", False):
                            notification.set_type("info")
                            notification.set_custom_color("#14c614")
                            notification.set_text("Changes have been saved.")
                            notification.show_window()
                        else:
                            notification.set_text("An error occurred.Please, try again later.")
                            notification.set_type("danger")
                            notification.show_window()

                touchable = None
                for tch in touchables:
                    res = tch.on_click(pos)
                    if res:
                        touchable = tch
                        break
                if touchable is not None:
                    if selected_cloak != _cosmetic_names.get(touchable.id):
                        selected_cloak = _cosmetic_names.get(touchable.id)
                        skin_uuid = api.get_data(f"https://minecraft-api.com/api/uuid/{skin_name_input.text.strip()}",
                                                 json_res=False).content.decode(encoding="utf-8")
                        skin_image, cloak_preview = asyncio.run(
                            fetch_skins(skin_uuid, PLAYER.nickname, selected_cloak,
                                        ignore_existing_file=True))

                        # api.post_data(CONSTANTS.api_url + f"player/?player={PLAYER.nickname}",
                        #               data={"cloak": PLAYER_DATA.get("cloak")})

        screen.fill((10, 10, 10))
        pygame.draw.rect(screen, "#181818", pygame.Rect(0, 68, width, height - 68))

        for button in buttons:
            button.render(screen, fonts[20])

        logo_image = icons['logo']
        screen.blit(pygame.transform.scale(logo_image, (48, 48)), (15, 15))
        screen.blit(logo_text, (85, 33))

        pygame.draw.rect(screen, "black",
                         pygame.Rect(235, 105,
                                     148, 276), border_radius=7)
        screen.blit(
            pygame.transform.smoothscale(skin_image if not show_cloak else cloak_preview, (128, 256)),
            (250, 120))

        draw_text("Skin name:", (420, 105), screen, PLAYER, fontsize=23)
        draw_text("Cosmetics:", (835, 105), screen, PLAYER, fontsize=23)

        for touchable in touchables:
            touchable.render(screen)

        for box in input_boxes:
            box.update()
            box.draw(screen)

        notification.draw(screen, None)
        pygame.display.flip()
        if (datetime.datetime.now() - last_input).seconds > 1 and not fetched:
            skin_uuid = api.get_data(f"https://minecraft-api.com/api/uuid/{skin_name_input.text.strip()}",
                                     json_res=False).content.decode(encoding="utf-8")
            skin_image, cloak_preview = asyncio.run(
                fetch_skins(skin_uuid, PLAYER.nickname, selected_cloak, ignore_existing_file=True))
            fetched = True
            print("fetched")
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
        Button("Home", 50, 32, (31, 31, 31), "white", 380, 30,
               (31, 31, 31), 2, font=fonts[14], high_light_color=(35, 35, 35), border_radius=5, ),
        Button("Skin", 50, 32, (10, 10, 10), "white", 450, 30,
               (31, 31, 31), 3, font=fonts[14], high_light_color=(35, 35, 35), border_radius=5, ),

    ]
    buttons[1].toggle_high_light()
    buttons[2].toggle_high_light()
    global screen
    logo_text = fonts[18].render("Minecraft 2D Multiplayer", False, "white")
    recent_news_text = fonts[16].render("Recent News", False, "white")

    posts, posts_data = get_posts_surface(fonts, icons)
    touchables = list()
    for p_i, post in enumerate(posts):
        touchables.append(TouchableOpacity(post, (30 + 415 * p_i, 475), p_i, True))
    notification = Notification("Unable to connect to the server. Try again later.", 4, (width, height),
                                notification_type="danger")
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
                            global PLAYER, session_stats, player_stats
                            PLAYER = Player((28, 60), (100, 12 * BLOCK_SIZE), 20, 20, 1,
                                            db_user[1])
                            api_data = api.get_data(
                                CONSTANTS.api_url + f"player/?player={PLAYER.nickname}&create=True&"
                                                    f"password={db_user[2]}").get("player")
                            global STORY_WORLD_COORD, PLAYER_DATA
                            PLAYER_DATA = api_data
                            if api_data.get("story_world_coord", None) is None:
                                STORY_WORLD_COORD = (1240, 2340)
                            else:
                                STORY_WORLD_COORD = api_data.get("story_world_coord")
                            player_stats = api_data.get(
                                "stats", {})
                            session_stats.update({"play_time": datetime.datetime.now()})

                        try:
                            client.connect(ADDR)
                        except Exception as _:
                            notification.show_window()
                            continue
                        on_screen = False
                        pygame.display.quit()
                        pygame.display.init()
                        screen = pygame.display.set_mode(SIZE)
                        break
                    elif btn.id == 1:
                        on_screen = False
                        pygame.quit()
                        exit(0)
                    elif btn.id == 3:
                        if db_user is None or not db_user[3]:
                            return log_in_screen()
                        else:
                            PLAYER = Player((28, 60), (100, 12 * BLOCK_SIZE), 20, 20, 1,
                                            db_user[1])
                            api_data = api.get_data(
                                CONSTANTS.api_url + f"player/?player={PLAYER.nickname}&create=True&"
                                                    f"password={db_user[2]}").get("player")
                            PLAYER_DATA = api_data
                            if api_data.get("story_world_coord", None) is None:
                                STORY_WORLD_COORD = (1240, 2340)
                            else:
                                STORY_WORLD_COORD = api_data.get("story_world_coord")
                            player_stats = api_data.get(
                                "stats", {})
                            session_stats.update({"play_time": datetime.datetime.now()})
                        on_screen = False
                        return customise_character()
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

        notification.draw(screen, None)
        pygame.display.flip()
        clock.tick(60)


start_screen()

sheet_path = "lib/assets/animations/Entities/player/"
if PLAYER_DATA.get("cloak", None) is not None:
    print("has cloak")
    PLAYER.has_cape = True
    PLAYER.cape = PLAYER_DATA.get("cloak", None)

print(sys.argv)
if len(sys.argv) >= 2:
    PLAYER.nickname = sys.argv[1]
print(PLAYER.nickname)
client.send(pickle.dumps(["id-update", PLAYER]))

running = True
player_id = PLAYER.nickname
players: dict[str, Player] = {}
players_images: dict[str, list[pygame.Surface]] = {}
players.update({player_id: PLAYER})

api.post_data(CONSTANTS.api_url + f"player/?player={PLAYER.nickname}&create=True",
              {"last_login": datetime.datetime.now().timestamp(), "last_logout": 0})

ENTITIES_UPDATE_DELAY = 150
last_entities_update = pygame.time.get_ticks()


async def main_screen():
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


async def load_skin(skin_name, nickname: str, save_directory: str, cape):
    if skin_name is None:
        skin_name = nickname
    res = api.get_data(f"https://mineskin.eu/skin/{skin_name}", json_res=False)
    shutil.copyfile(f"lib/users/skin/raw_steve.png", f"lib/temp/raw_skins/{nickname}.png")
    with open(f"lib/temp/raw_skins/{nickname}.png", "wb") as f:
        f.write(res.content)
    await generate_animations(f"lib/temp/raw_skins/{nickname}.png", save_directory,
                              cape)


asyncio.run(run_multiple_tasks(
    [main_screen(), load_skin(PLAYER_DATA.get("skin_uuid", None), PLAYER.nickname, sheet_path, PLAYER.cape)]))

print(PLAYER.nickname)
PLAYER_IMAGES = load_player_images(sheet_path)
players_images.update({PLAYER.nickname: PLAYER_IMAGES})


def get_npc():
    return [CEBK, GREETER, KIRA, *NPC_FILLERS]


CEBK = Npc((28, 60), (100, 23 * BLOCK_SIZE), 20, 20, 1,
           "cebk", speed=1.75, jump_height=1.5)
KIRA = Npc((28, 60), (100, 23 * BLOCK_SIZE), 20, 20, 1,
           "kira", speed=1.75, jump_height=1.5)

GREETER = Npc((28, 60), (100, 23 * BLOCK_SIZE), 20, 20, 1,
              "greeter")

NPC_FILLERS = [Npc((28, 60), (random.randint(CASTLE_AREA[0][0], CASTLE_AREA[1][0]), CASTLE_AREA[0][1]), 20, 20, 1,
                   FRACTIONS[i % len(FRACTIONS)], space_filler=True, dimension="abyss") for i in
               range(len(FRACTIONS) * 2)]

with open("lib/storage/story_characters.json", "r", encoding="utf-8") as f:
    data: dict = json.load(f)
    for key in list(data.keys()):
        eval(f"{key.upper()}.set_coord({data[key].get('x')}, {data[key].get('y')})")
        eval(f"{key.upper()}.set_dimension('{data[key].get('dimension')}')")

true_scroll = [0, 0]
hold_start = datetime.datetime.now()
scroll = [0, 0]
SCREEN.set_story_world_pos(STORY_WORLD_COORD)
gm_map = []
add_to_background = False
collisions_before = {'top': False, 'bottom': False, 'right': False, 'left': False}

STORY_TASKS = StoryTasks(PLAYER_DATA.get("active_tasks", {}))

while running:
    ins, outs, ex = select.select([client], [], [], 0)

    for inm in ins:
        try:
            event = pickle.loads(inm.recv(4096))
            if event[0] == 'id-update':
                player_id = event[1]

            elif event[0] == 'players-update' and event[1] != player_id:
                if event[1] not in list(players.keys()):
                    dir_path = f"lib/users/{event[1]}/"
                    if not os.path.exists(dir_path):
                        os.mkdir(dir_path)
                    asyncio.run(load_skin(event[1], event[1], dir_path, event[2].cape))
                    print(event[2].cape)
                    imgs = load_player_images(dir_path)
                    players_images.update({event[1]: imgs})

                players.update({event[1]: event[2]})
            elif event[0] == 'player-disconnect':
                players = {key: val for key, val in players.items() if key != event[1]}

            elif event[0] == "block-id-update":
                pos = event[1]
                _value = event[2]
                if SCREEN.screen != "abyss":
                    game_map["map"][pos[1]][pos[0]] = {"block_id": _value}
                else:
                    gm_map[pos[1]][pos[0]] = {"block_id": _value}

        except pickle.UnpicklingError as e:
            pass
        except Exception as e:
            print(f"RAISED EXCEPTION - {e}")

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
            session_stats.update({"play_time": (datetime.datetime.now() - session_stats.get("play_time")).seconds})
            save_stats(PLAYER.nickname, session_stats, CONSTANTS, player_stats)
            exit(0)
        if not SCREEN.paused:
            if event.type == KEYDOWN:
                if event.key == K_LEFT or event.key == K_a:
                    moving_left = True
                elif event.key == K_RIGHT or event.key == K_d:
                    moving_right = True
                elif event.key == K_UP:
                    jumping = True
                elif event.key == K_SPACE:
                    PLAYER.vertical_momentum -= 10
                    jumping = True

                elif event.key == K_c:
                    print(f"[PLAYER COORD] {PLAYER.rect}")
                    print(f"[MOUSE COORD] {pygame.mouse.get_pos()}")

                elif event.key == K_r:
                    SCREEN.set_action_bar("Задачи обновлены.", 3)
                elif event.key == K_g:
                    add_to_background = not add_to_background
                    print(add_to_background)
            if event.type == KEYUP:
                if event.key == K_LEFT:
                    moving_left = False
                elif event.key == K_RIGHT:
                    moving_right = False
                elif event.key == K_UP:
                    jumping = False

        if event.type == KEYDOWN:
            if event.key == K_k:
                SCREEN.toggle_rep()
                moving_left = moving_right = jumping = False

            elif event.key == K_ESCAPE:
                SCREEN.call_close_window()

        if event.type == MOUSEMOTION:
            SCREEN.set_mouse_pos(event.pos)
        if event.type == MOUSEBUTTONDOWN:
            hold_start = datetime.datetime.now()
            SCREEN.set_hold_button("left" if event.button == 1 else "right" if event.button == 3 else "middle", True,
                                   PLAYER)
            for npc in get_npc():
                stop = npc.on_click(event.pos, event.button, SCREEN, PLAYER, scroll)
                if stop:
                    moving_left = moving_right = jumping = False

            if SCREEN.screen == 'abyss':
                if event.button == 3:
                    colliding_objects, gm_map, placed, placed_id = on_right_click(event, colliding_objects, scroll,
                                                                                  gm_map,
                                                                                  PLAYER,
                                                                                  SCREEN,
                                                                                  session_stats)
                    if placed:
                        client.send(
                            pickle.dumps(
                                ["block-placed" if not add_to_background else "block-placed-background",
                                 [(event.pos[0] + scroll[0]) // 32, (event.pos[1] + scroll[1]) // 32],
                                 placed_id]))

        if event.type == MOUSEBUTTONUP:
            SCREEN.set_hold_button("left" if event.button == 1 else "right" if event.button == 3 else "middle",
                                   False, PLAYER)
        if event.type == MOUSEWHEEL:
            if not SCREEN.paused:
                PLAYER.set_selected_slot(PLAYER.selected_inventory_slot - (-1 if event.y < 0 else 1))

    current_time = pygame.time.get_ticks()
    if current_time - ENTITIES_UPDATE_DELAY > last_entities_update:
        PLAYER.update_frame(PLAYER_IMAGES)
        for npc in get_npc():
            npc.update_frame()
        last_entities_update = current_time
    PLAYER.set_size(28, 60)

    screen.fill(CONSTANTS.sky)

    if SCREEN.screen == "lobby":
        screen.blit(pygame.transform.scale(icons['Ocean_background_6'], SIZE), (0, 0))
    else:
        screen.fill((17, 36, 42))

    colliding_objects = list()
    if SCREEN.screen == 'lobby':
        PLAYER.dimension = "lobby"
        possible_x = [i for i in range(WIDTH // BLOCK_SIZE + 2)]
        possible_y = [i for i in range(HEIGHT // BLOCK_SIZE)]
        if gm_map != lobby_map.get("map"):
            gm_map: list = lobby_map.get("map")
        scroll = [0, 0]
    elif SCREEN.screen == 'abyss':
        PLAYER.dimension = "abyss"
        true_scroll[0] += (PLAYER.rect.x - true_scroll[0] - WIDTH // 2 - PLAYER.rect.w // 2) / 20
        true_scroll[1] += (PLAYER.rect.y - true_scroll[1] - HEIGHT // 2 - PLAYER.rect.h // 2) / 20
        scroll = true_scroll.copy()

        scroll[0] = int(scroll[0])
        scroll[1] = int(scroll[1])
        if gm_map == lobby_map.get("map"):
            gm_map: list = game_map.get("map")

        possible_x = [num if abs(PLAYER.rect.x - num * BLOCK_SIZE) <= WIDTH // 2 + (2 * BLOCK_SIZE) else 0 for num in
                      range(len(gm_map[0]))]
        possible_y = [num if abs(PLAYER.rect.y - num * BLOCK_SIZE) <= WIDTH // 2 else 0 for num in range(128)]

        possible_x = list(filter((0).__ne__, possible_x))
        possible_y = list(filter((0).__ne__, possible_y))

    for tile_y in possible_y:
        for tile_x in possible_x:
            block: dict = gm_map[tile_y][tile_x]
            block_id = block.get("block_id", "0")
            if block_id.count(":"):
                block_id, state = block_id.split(":")
            if block.get("background_block_id", None) is not None and block_id == "0":
                block_id = block.get("background_block_id", "3")
            percentage = 0
            if block.get("percentage", 0.0) > 0:
                percentage = math.floor(float(block.get("percentage", 0.0)) / 10)

            if block_id != "0":
                if block_id == "1" and get_block_from_coords(tile_y - 1, tile_x, gm_map).get("block_id") != "0":
                    gm_map[tile_y][tile_x] = {"block_id": "2"}
                    block_id = "2"
                elif block_id == "2" and get_block_from_coords(tile_y - 1, tile_x, gm_map).get(
                        "block_id") == "0" and (
                        get_block_from_coords(tile_y, tile_x - 1, gm_map).get(
                            "block_id") == "1" or
                        get_block_from_coords(tile_y, tile_x + 1, gm_map).get("block_id") == "1"):
                    if random.randint(0, 5000) == 4:
                        gm_map[tile_y][tile_x] = {"block_id": "1"}
                        block_id = "1"
                        # Send data to server
                        client.send(pickle.dumps(["block-placed", [tile_x, tile_y], "1"]))

                block_data = blocks_data[block_id]

                search = block_data["item_id"] if SCREEN.screen == 'lobby' else "abyss-" + block_data[
                    "item_id"] if SCREEN.screen == "abyss" else "stone"
                if block_data['item_id'] == "bed":
                    if gm_map[tile_y][tile_x - 1].get("block_id") == "365":
                        image = images.get("bed_bottom")
                    elif gm_map[tile_y][tile_x + 1].get("block_id") == "365":
                        image = images.get("bed_top")
                    else:
                        image = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE), SRCALPHA).convert()
                        gm_map[tile_y][tile_x] = {"block_id": "0"}
                elif block_data['item_id'].count("door"):
                    color = images.get(block_data['item_id'] + "_top").get_at((0, 0))
                    if state == "1":
                        if gm_map[tile_y][tile_x].get("open", False):
                            image = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE), SRCALPHA)
                            pygame.draw.line(image, color, (0, 0), (0, BLOCK_SIZE), width=2)
                        else:
                            if gm_map[tile_y + 1][tile_x].get("block_id").count(block_id):
                                image = images.get(block_data['item_id'] + "_top")
                            else:
                                image = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE), SRCALPHA).convert()
                                gm_map[tile_y][tile_x] = {"block_id": "0"}

                    elif state == "2":
                        if gm_map[tile_y - 1][tile_x].get("open", False):
                            image = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE), SRCALPHA)
                            pygame.draw.line(image, color, (0, 0), (0, BLOCK_SIZE), width=2)
                        else:
                            if gm_map[tile_y - 1][tile_x].get("block_id").count(block_id):
                                image = images.get(block_data['item_id'] + "_bottom")
                            else:
                                image = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE), SRCALPHA).convert()
                                gm_map[tile_y][tile_x] = {"block_id": "0"}

                else:
                    image = images.get(search, images.get(block_data['item_id']))
                image = image.convert_alpha()
                if block.get("background", False):
                    darken_percent = .45
                    dark = pygame.Surface(image.get_size()).convert_alpha()
                    dark.fill((0, 0, 0, darken_percent * 255))
                    image.blit(dark, (0, 0))

                screen.blit(pygame.transform.scale(image, (BLOCK_SIZE, BLOCK_SIZE)),
                            (tile_x * BLOCK_SIZE - scroll[0], tile_y * BLOCK_SIZE - scroll[1]))

                mouse_coord = SCREEN.mouse_pos
                mrect = pygame.Rect(mouse_coord[0], mouse_coord[1], 1, 1)
                rect = pygame.Rect(tile_x * 32 - scroll[0], tile_y * 32 - scroll[1], 32, 32)
                close = is_close(mouse_coord[0] + scroll[0], mouse_coord[1] + scroll[1], PLAYER.rect.x,
                                 PLAYER.rect.y, 4)

                if mrect.colliderect(rect) and close:
                    pygame.draw.rect(screen, (232, 115, 104), rect, width=2)

                if block_id not in NOT_COLLIDING_BLOCKS and not (
                        block.get("background_block_id", None) is not None and block.get("block_id",
                                                                                         "0") == "0") and not \
                        gm_map[tile_y - 1 if block_id in ["324"] and state == "2" else tile_y][tile_x].get("open",
                                                                                                           False):
                    block_rect = pygame.Rect(tile_x * BLOCK_SIZE, tile_y * BLOCK_SIZE,
                                             BLOCK_SIZE,
                                             BLOCK_SIZE)
                    colliding_objects.append(block_rect)

                if percentage:
                    image = block_breaking.get(f"{percentage if percentage < 10 else 9}")
                    image.set_colorkey((0, 0, 0), RLEACCEL)
                    screen.blit(image, (tile_x * 32 - scroll[0], tile_y * 32 - scroll[1]))

    movement = [0, 0]
    if moving_right or moving_left:
        if PLAYER.condition != 'run':
            PLAYER.change_condition('run')
    else:
        if PLAYER.condition != 'idle':
            PLAYER.change_condition()
    if moving_right and PLAYER.rect.x + PLAYER.rect.w < len(gm_map[0]) * BLOCK_SIZE:
        movement[0] += 2
        PLAYER.moving_direction = 'right'
    if moving_left and PLAYER.rect.x > 0:
        movement[0] -= 2
        PLAYER.moving_direction = 'left'

    if jumping and PLAYER.air_timer < 10 and collisions_before[
        "bottom"] and pygame.time.get_ticks() - PLAYER.last_landing_time > 75:
        PLAYER.vertical_momentum -= 9.5

    movement[1] += PLAYER.vertical_momentum
    PLAYER.vertical_momentum = PLAYER.vertical_momentum + 0.5 if PLAYER.vertical_momentum + 0.5 <= 3 else 3

    PLAYER.rect, collisions = move(PLAYER.rect, movement, colliding_objects)

    move_npc(get_npc(), colliding_objects, move, PLAYER, SCREEN, BLOCK_SIZE, possible_x, possible_y, CASTLE_AREA)
    if not collisions['bottom']:
        PLAYER.air_timer += 1
    else:
        PLAYER.air_timer = 0

        if not collisions_before['bottom']:
            PLAYER.last_landing_time = pygame.time.get_ticks()

    collisions_before = deepcopy(collisions)

    for key in players:
        player = players[key]
        # pygame.draw.rect(screen, "white", player.rect)
        if player.dimension == PLAYER.dimension:
            player.draw(screen, scroll, players_images.get(player.nickname, {}))
            nick_surf = fonts[12].render(player.nickname, False,
                                         "gray" if player.nickname != PLAYER.nickname else "white")
            nick_rect = pygame.Rect(player.rect.x - player.rect.w // 4 - nick_surf.get_width() // 4 - scroll[0],
                                    player.rect.y - nick_surf.get_height() - 5 - scroll[1],
                                    player.rect.w + nick_surf.get_width(),
                                    nick_surf.get_height() + 5)
            draw_rect_alpha(screen, (17, 36, 42, 127),
                            nick_rect)
            screen.blit(nick_surf,
                        (nick_rect.centerx - nick_surf.get_width() // 2, nick_rect.y + 3))

    for npc in get_npc():
        if SCREEN.screen == npc.dimension:
            if npc.rect.x // BLOCK_SIZE in possible_x and npc.rect.y // BLOCK_SIZE in possible_y:
                npc.draw(screen, scroll)
            else:
                if npc.hide and npc.rect.y > 0:
                    print(f"hide npc - {npc.name}")
                    npc.rect.y = -300
                    SCREEN.edit_characters(npc.name, "y", -300)

    if SCREEN.hold_buttons["left"] and SCREEN.screen == 'abyss':
        colliding_objects, gm_map, hold_start, _, _block_broken, pos = on_left_click(SCREEN.mouse_pos,
                                                                                     colliding_objects,
                                                                                     scroll,
                                                                                     gm_map, PLAYER, hold_start,
                                                                                     blocks_data,
                                                                                     [],
                                                                                     session_stats, images)

        if _block_broken:
            client.send(
                pickle.dumps(["block-break", [*pos]]))
    if SCREEN.screen == 'abyss':
        draw_inventory(screen, PLAYER, images, blocks_data, SCREEN)

    if SCREEN.show_dialog:
        img = pygame.transform.scale(images['dialog_window'], (WIDTH * 0.675, HEIGHT * 0.75))
        screen.blit(img,
                    (screen.get_width() // 2 - img.get_width() // 2, screen.get_height() // 2 - img.get_height() // 2))
        draw_dialog_window(screen, SCREEN, fonts[24], PLAYER, get_npc())

    elif SCREEN.show_rep:
        draw_rep(screen, PLAYER_DATA.get("reputation", {}), images, icons, SIZE)

    elif SCREEN.show_tasks:
        draw_tasks(screen, STORY_TASKS.tasks, images, icons, PLAYER)

    SCREEN.render_action_bar(screen, PLAYER)

    _npc, _field, _value = SCREEN.story(PLAYER, get_npc())
    if _npc is not None:
        eval(f"""{_npc.upper()}.on_update("{_field}", "{_value}")""")
    pygame.display.flip()

    clock.tick(60)
    if list(players.keys()).count(player_id) > 0:
        client.send(pickle.dumps(["player-update", player_id, PLAYER.server_data()]))
