import datetime
import json
import math
import random
import noise
import pygame

from lib.functions.blocks import get_block_data_by_name, calculate_breaking_time


def generate_chunks(blocks_data, y_max, quantity_of_chunks, seed, dimension):
    x_max = 8 * quantity_of_chunks
    game_map = [[{"block_id": "0"} for _ in range(x_max)] for _ in range(y_max)]

    trees = [
        """ 1111
 1112111
111121111
    2
    2"""
    ]

    if dimension == 'overworld':
        for tile_y in range(y_max):
            for tile_x in range(x_max):

                generate_vines = random.randint(1, 500) == 4
                upper_block = "1"
                fill_block = "2"

                if tile_y == 0:
                    block = get_block_data_by_name(blocks_data, 'stone')
                    game_map[tile_y][tile_x] = {"block_id": block['numerical_id']} if block is not None else {
                        "block_id": '0'}
                elif 1 <= tile_y <= 60:
                    value = random.randint(0, 1000)
                    block_id = 0
                    height = math.floor(noise.pnoise2(tile_x * 0.1, tile_y * 0.1) * (seed ** 0.5))
                    if height < seed ** 0.5 * 0.1:
                        if 925 <= value <= 1000:
                            block_id = ore_generator(tile_y, y_max)
                        else:
                            block_id = get_block_data_by_name(blocks_data, 'stone')['numerical_id']

                    game_map[tile_y][tile_x] = {"block_id": block_id.__str__()}
                elif 60 <= tile_y <= 64:
                    # block_id = get_block_data_by_name(blocks_data, 'dirt')['numerical_id']

                    game_map[tile_y][tile_x] = {"block_id": fill_block}
                elif 65 <= tile_y <= 70:
                    # value = random.randint(1, 1000)
                    height = math.floor(noise.pnoise1(tile_x * 0.1, repeat=9999999) * (seed ** 0.5))
                    if tile_y <= (70 + 65) // 2 - height and game_map[tile_y][tile_x].get("block_id") == "0":
                        game_map[tile_y][tile_x] = {"block_id": upper_block}
                if generate_vines:
                    if 65 <= tile_y <= 70 and game_map[tile_y - 1][tile_x].get("block_id") in [upper_block,
                                                                                               fill_block] and \
                            game_map[tile_y][tile_x].get("block_id") == "0":
                        value = random.randint(0, 100)
                        if value < 12:
                            length = random.randint(2, 3)
                            for y_adder in range(length):
                                game_map[tile_y + y_adder][tile_x] = {"block_id": "81"}
                # Деревья
                else:
                    if game_map[tile_y][tile_x - 5].get("block_id") == "0" and game_map[tile_y - 1][tile_x - 5].get(
                            "block_id") != "0" \
                            and 70 >= tile_y >= 65:
                        value = random.randint(1, 1000)
                        if 0 <= value <= 100:
                            tree = random.choice(trees)
                            tree = tree.replace(' ', "0")
                            tree = tree.split("\n")
                            tree = tree[::-1]

                            for y_adder in range(len(tree)):
                                for x_adder in range(len(tree[2])):
                                    try:
                                        current = tree[y_adder][x_adder]
                                        if current != "0":
                                            game_map[tile_y + y_adder][
                                                tile_x - 5 - len(tree[
                                                                     0]) + x_adder] = {
                                                "block_id": "18"} if current == "1" \
                                                else {"block_id": "17"}
                                    except IndexError:
                                        # мы вышли за границу карты
                                        pass

    elif dimension == 'nether':
        for tile_y in range(y_max):
            for tile_x in range(x_max):

                if tile_y == 0:
                    block = get_block_data_by_name(blocks_data, 'netherrack')
                    game_map[tile_y][tile_x] = {"block_id": block['numerical_id']} if block is not None else {
                        "block_id": '0'}
                elif 1 <= tile_y <= 60:
                    value = random.randint(0, 1000)
                    block_id = 0
                    if 0 <= value <= 924:
                        block_id = get_block_data_by_name(blocks_data, 'netherrack')['numerical_id']
                    elif 925 <= value <= 1000:
                        block_id = ore_generator(tile_y, y_max, dimension='nether')
                    game_map[tile_y][tile_x] = {"block_id": block_id.__str__()}
                elif 60 <= tile_y <= 64:
                    block_id = get_block_data_by_name(blocks_data, 'netherrack')['numerical_id']
                    game_map[tile_y][tile_x] = {"block_id": block_id.__str__()}
                elif 65 <= tile_y <= 70:
                    height = math.floor(noise.pnoise1(tile_x * 0.1, repeat=9999999) * (seed ** 0.5))

                    if tile_y <= (70 + 65) // 2 - height:
                        game_map[tile_y][tile_x] = {"block_id": "87"}
                    # else:
                    #     if 0 <= value <= 950 and game_map[tile_y - 1][tile_x] != "0":
                    #         game_map[tile_y][tile_x] = "11"
                elif 95 <= tile_y <= 128:
                    block_id = get_block_data_by_name(blocks_data, 'netherrack')['numerical_id']
                    game_map[tile_y][tile_x] = {"block_id": block_id.__str__()}

    if dimension == 'nether':
        for i in range(6):
            y = 90 + i
            game_map[y] = game_map[65 + (5 - i)][:-1]

    return game_map[::-1]


def ore_generator(y, y_max, dimension='overworld') -> str:
    if dimension == 'overworld':
        possible_blocks = [69]
        if y <= y_max // 2:
            possible_blocks.append(15)
        if y <= y_max // 4:
            possible_blocks.append(14)
            possible_blocks.append(21)
            possible_blocks.append(129)
            possible_blocks.append(68)

        if y <= y_max // 8:
            possible_blocks.append(56)
            possible_blocks.append(73)
    elif dimension == 'nether':
        possible_blocks = [153]
    else:
        possible_blocks = [16]
    return str(random.choice(possible_blocks))


def is_close(x, y, x0, y0, radius) -> bool:
    return ((x - x0) ** 2 + (y - y0) ** 2) <= (radius * 32) ** 2


def edit_by_coords(x, y, value):
    with open("../storage/game_map.json", "r") as f:
        data = json.load(f)

    game_map = data.get("map")
    game_map[y][x] = value

    data.update({"map": game_map})

    with open("../storage/game_map.json", "w") as f:
        json.dump(data, f)


# edit_by_coords(43, 71, {"block_id": "0"})


def on_right_click(event, map_objects, scroll, game_map, player, screen,
                   session_stats):
    pos = event.pos
    x = pos[0]
    y = pos[1]
    # максимальная дистанция 4 блока (сторона 32)
    close = is_close(x + scroll[0], y + scroll[1], player.rect.x, player.rect.y, 4)
    if close:
        value_x = (x + scroll[0]) // 32
        value_y = (y + scroll[1]) // 32
        try:
            tile = game_map[value_y][value_x].get("block_id")
            # игрок кликнул по "воздуху" и рядом с "воздухом есть блок"
            if tile in ["0", "9"]:
                if game_map[value_y + 1][value_x].get("block_id") != "0" or game_map[value_y - 1][value_x].get(
                        "block_id") != "0" \
                        or game_map[value_y][value_x + 1].get("block_id") != "0" or game_map[value_y][value_x - 1].get(
                    "block_id") != "0":
                    selected = player.inventory[0][player.selected_inventory_slot]
                    if selected is not None and selected['type'] == 'block':
                        if game_map[value_y][value_x + 1].get("block_id") == "0" and selected["item_id"] == "bed":
                            game_map[value_y][value_x] = {"block_id": selected['numerical_id']}
                            game_map[value_y][value_x + 1] = {"block_id": selected['numerical_id']}
                        elif selected["item_id"] != "bed":
                            game_map[value_y][value_x] = {"block_id": selected['numerical_id']}

                        map_objects.append(pygame.Rect(value_x * 32, value_y * 32, 32, 32))
                        player.remove_from_inventory(player.selected_inventory_slot, 1)
                        session_stats.update({"blocks_placed": session_stats.get('blocks_placed', 0) + 1})

            elif tile == "58":
                screen.toggle_inventory("crafting_table")
        except IndexError:
            print('доделать!!!!! (lib/models/map.py), line: 26')

    return map_objects, game_map


def on_left_click(pos, map_objects, scroll, game_map, player, hold_start, blocks_data,
                  falling_items, session_stats: dict,
                  images: dict[str, pygame.Surface]):
    x = pos[0]
    y = pos[1]
    # максимальная дистанция 4 блока (сторона 32)
    close = is_close(x + scroll[0], y + scroll[1], player.rect.x, player.rect.y, 4)
    block_broken = False
    if close:
        value_x = (x + scroll[0]) // 32
        value_y = (y + scroll[1]) // 32
        try:
            data = game_map[value_y][value_x]
            tile = data.get("block_id", "0")
            if tile != "0" and not tile.count(":"):

                block_data = blocks_data[tile]
                if type(block_data) == dict:
                    if block_data.get('diggable', 0):
                        breaking_time = calculate_breaking_time(block_data, player)
                        now = datetime.datetime.now()
                        if now - hold_start >= datetime.timedelta(seconds=breaking_time):
                            game_map[value_y][value_x] = {"block_id": '0'}
                            if tile != "58":
                                map_objects.remove(pygame.Rect(value_x * 32, value_y * 32, 32, 32))
                            hold_start = now

                            num_id = tile
                            if tile == "3":
                                num_id = "4"
                            elif tile == '16':
                                num_id = '263'
                            elif tile == "21":
                                num_id = "351"
                            elif tile == '56':
                                num_id = "264"
                            elif tile == "73":
                                num_id = "331"
                            elif tile == "129":
                                num_id = "388"

                            # block_image = images[block_data["item_id"]]
                            # color = block_image.get_at((block_image.get_width() // 2, block_image.get_height() // 2))
                            # position = (x * 32 // 32, y * 32 // 32)
                            # for _ in range(10):
                            #     velocity = [random.randint(0, 20) / 10 - 1, -1]
                            #     timer = random.randint(2, 5)
                            #
                            #     screen.particles.add_particle(position, velocity, timer, color)

                            x += scroll[0]
                            y += scroll[1]
                            x //= 32
                            x *= 32
                            x += 8
                            y //= 32
                            y *= 32

                            falling_items.append({
                                "direction": "down",
                                "x": x,
                                "y": y,
                                "numerical_id": num_id
                            })
                            session_stats.update({"blocks_mined": session_stats.get('blocks_mined', 0) + 1})
                            if tile in ["16", "21", "73", "129", "56"]:
                                for _ in range(random.randint(0, 5)):
                                    falling_items.append({
                                        "direction": "down",
                                        "x": x,
                                        "y": y,
                                        "numerical_id": "998"
                                    })

                            block_broken = True
                        else:
                            time_spent = now - hold_start
                            percentage = (time_spent / datetime.timedelta(
                                seconds=breaking_time)) * 100
                            game_map[value_y][value_x] = {"block_id": f"{tile}", "percentage": percentage}

        except IndexError:
            print('доделать!!!!! (lib/models/map.py), line: 26')

    return map_objects, game_map, hold_start, falling_items, block_broken
