import math
import random
import noise

from lib.functions.blocks import get_block_data_by_name


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
        possible_blocks = [16]
        if y <= y_max // 2:
            possible_blocks.append(15)
        if y <= y_max // 4:
            possible_blocks.append(14)
            possible_blocks.append(21)
            possible_blocks.append(129)
        if y <= y_max // 8:
            possible_blocks.append(56)
            possible_blocks.append(73)
    elif dimension == 'nether':
        possible_blocks = [153]
    else:
        possible_blocks = [16]
    return str(random.choice(possible_blocks))
