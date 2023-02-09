import json
import os

import pygame
from lib.functions.text import blit_text
from lib.functions.map_actions import generate_chunks


def get_maps():
    with open("lib/storage/lobby_map.json", "r") as lmf:
        lobby_map = json.load(lmf)

    with open("lib/storage/blocks.json", "r") as bdf:
        blocks = json.load(bdf)

    with open("lib/storage/game_map.json", "r") as gmf:
        game_map = json.load(gmf)
        if game_map == {} or game_map.get("map", None) is None:
            print("generate story map")
            game_map.update({"map": generate_chunks(blocks, 128, 125, 355, "overworld")})

            gmf.close()
            with open("lib/storage/game_map.json", "w") as f:
                json.dump(game_map, f)

    return lobby_map, game_map, blocks


def get_images(blocks_data: dict):
    images = dict()
    icons = dict()
    mob_images = dict()
    block_breaking = dict()

    for file in os.listdir("lib/assets/animations/block_breaking"):
        if file.endswith(".png"):
            index = file[file.index("(") + 1]
            block_breaking.update(
                {index: pygame.image.load(os.path.join("lib/assets/animations/block_breaking", file))})

    for block in list(blocks_data.values()):
        if os.path.exists(f"lib/assets/abyss/{block['image_root']}"):
            images.update({"abyss-" + block['item_id']: pygame.image.load(f"lib/assets/abyss/{block['image_root']}")})
        if os.path.exists(f"lib/assets/{block['image_root']}"):
            images.update({block['item_id']: pygame.image.load(f"lib/assets/{block['image_root']}")})
    images.update({"main_screen_bg": pygame.image.load("lib/assets/main_screen_bg.png")})
    images.update({"launcher_background": pygame.image.load("lib/assets/launcher_background.jpg")})
    images.update({"world_select_bg": pygame.image.load("lib/assets/world_select_bg.jpg")})
    images.update({"overworld_background": pygame.image.load("lib/assets/overworld_background.png")})
    images.update({"no_textures": pygame.image.load("lib/assets/no_textures.webp")})
    images.update({"bed_top": pygame.image.load("lib/assets/bed-top.png")})
    images.update({"bed_bottom": pygame.image.load("lib/assets/bed-bottom.png")})

    for file in os.listdir("lib/assets/items"):
        if file.endswith(".png"):
            images.update({file.split(".")[0]: pygame.image.load(f"lib/assets/items/{file}")})
    for file in os.listdir("lib/assets/windows"):
        if file.endswith(".png"):
            images.update({file.split(".")[0]: pygame.image.load(f"lib/assets/windows/{file}")})

    for file in os.listdir("lib/assets/icons"):
        if file.endswith(".webp") or file.endswith(".png"):
            icons.update({f"{file.split('.')[0]}": pygame.image.load(f"lib/assets/icons/{file}")})

    for file in os.listdir("lib/assets/developers"):
        if file.endswith(".webp") or file.endswith(".png"):
            icons.update({f"{file.split('.')[0]}": pygame.image.load(f"lib/assets/developers/{file}")})

    icons.update({"sun": pygame.image.load("lib/assets/sun.png")})
    icons.update({"moon": pygame.image.load("lib/assets/moon.png")})

    # for folder in os.listdir("lib/assets/animations/mobs/"):
    #     if folder != ".DS_Store":
    #         mob_images.update({folder: {}})
    #         for file in os.listdir(f"lib/assets/animations/mobs/{folder}"):
    #             if file != ".DS_Store":
    #                 mob_images[folder][file.split(".")[0]] = pygame.image.load(
    #                     f"lib/assets/animations/mobs/{folder}/{file}")
    #
    # mob = CaveMonster(20, 20, 1, 2, 1, True, False, (0, 0), 32, 64, 8)
    # mob.cut_sheet(mob_images["cave_monster"]["idle"], 4, 1, "idle", 120, 50)
    # mob_images['cave_monster']['idle'] = mob.images
    # mob.cut_sheet(mob_images["cave_monster"]["walk"], 6, 1, "walk", 120, 45)
    # mob_images['cave_monster']['walk'] = mob.images
    # mob.cut_sheet(mob_images["cave_monster"]["hurt"], 4, 1, "hurt", 120, 50)
    # mob_images['cave_monster']['hurt'] = mob.images
    # mob.cut_sheet(mob_images["cave_monster"]["death"], 4, 1, "death", 120, 50)
    # mob_images['cave_monster']['death'] = mob.images
    # mob.cut_sheet(mob_images["cave_monster"]["attack"], 4, 1, "attack", 120, 50)
    # mob_images['cave_monster']['attack'] = mob.images

    return images, icons, mob_images, block_breaking


def get_posts_surface(fonts, icons):
    with open("lib/temp/recent_posts.json", "r") as f:
        data = json.load(f)

    res = list()

    for key in data:
        surface = pygame.Surface((390, 255))
        surface.fill((32, 31, 29))
        post = data[key]
        text = post.get("text", "")
        author = post.get("author", "")
        image_path = post.get("image", None)
        text_color = (121, 120, 118)

        temp_surf = pygame.Surface((382, fonts[14].get_height() * 2))
        blit_text(temp_surf, text, (0, 0), fonts[14], color=pygame.Color(text_color))

        if image_path is not None:
            image = pygame.image.load(image_path)
            x, y = image.get_rect().center
            img_width, img_height = image.get_size()
            surface.blit(image, (0, 0), (x - img_width // 4, y - img_height // 4, 390, 166))
        temp_surf.set_colorkey((0, 0, 0))
        author_surf = fonts[14].render(f"Posted by", False, text_color)
        surface.blit(author_surf, (4, 170 + fonts[14].get_height() * 2 + 25))
        surface.blit(temp_surf, (4, 170))
        author_icon = "subvius" if author == "Артур" else "artur_huzhin" if author == 'Артур Хужин' else "elisha"
        # author_icon = "subvius"
        surface.blit(pygame.transform.scale(icons[author_icon], (16, 16)),
                     (4 + author_surf.get_width() + 4, 170 + fonts[14].get_height() * 2 + 23))
        surface.blit(fonts[14].render(author.capitalize(), False, text_color),
                     (4 + author_surf.get_width() + 24, 170 + fonts[14].get_height() * 2 + 25))

        pygame.draw.rect(surface, (36, 114, 206), pygame.Rect(300, 170 + fonts[14].get_height() * 2 + 18, 80, 30))
        surface.blit(fonts[14].render("Read more", False, "white"), (300 + 4, 170 + fonts[14].get_height() * 2 + 26))

        res.append(surface)

    return res, data


def load_player_images(sheet_path):
    images = dict()
    for file in os.listdir(sheet_path):
        if file.endswith(".png") and file.count("-"):
            anim_type = file.split("-")[0]
            if not list(images.keys()).count(anim_type):
                images.update({anim_type: []})

            images[anim_type].append(pygame.image.load(os.path.join(sheet_path, file)))

    return images
