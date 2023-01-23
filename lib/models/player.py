import math

import pygame

from lib.func.blocks import get_block_data_by_name
from lib.models.sound import Sound


class Player:
    def __init__(self, rect, image, inventory, selected_inventory_slot, hp, max_hp):
        self.rect: pygame.Rect = rect
        self.width: int = 50
        self.image = image
        self.inventory: list = inventory
        self.creative_inventory_page = "search"
        self.selected_inventory_slot: int = selected_inventory_slot
        self.hp: float = hp
        self.jump_start = None
        self.max_hp: int = max_hp
        self.images = {
            "idle": [],
            'run': [],
            'throw': [],
        }
        self.frame = 0
        self.condition = "run"
        self.moving_direction = "right"
        self.is_dead = False
        self.exp = 6
        self.level = 0
        self.game_mode = "survival"
        self.in_water = False

    def cut_sheet(self, sheet, columns, rows, animation_type):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.width * i + 29 * i, (self.width - 2) * j)
                image = sheet.subsurface(pygame.Rect(
                    frame_location, (self.width, 70)))
                self.images[animation_type].append(image)

    def add_to_inventory(self, item: dict, blocks_data) -> bool:
        block = get_block_data_by_name(blocks_data, item['item_id'])
        for i_y, slot_y in enumerate(self.inventory):
            for i_x, slot_x in enumerate(slot_y):
                if slot_x is None:
                    self.inventory[i_y][i_x] = item
                    return True
                else:
                    if slot_x.get("item_id") == item.get("item_id") and slot_x.get("quantity") < block.get(
                            "max_stack_size"):
                        slot_x['quantity'] += item['quantity']

                        if slot_x['quantity'] > block.get("max_stack_size"):
                            item['quantity'] = slot_x['quantity'] - block.get("max_stack_size")
                            slot_x['quantity'] = block.get("max_stack_size")
                            self.inventory[i_y][i_x] = slot_x
                        else:
                            self.inventory[i_y][i_x] = slot_x
                            return True
        return False

    def change_game_mode(self, game_mode: str = "survival"):
        if not self.is_dead:
            self.game_mode = game_mode

    def update_image(self):
        self.frame = (self.frame + 1) % len(self.images[self.condition])
        self.image = self.images[self.condition][self.frame]

    def change_condition(self, condition):
        self.condition = condition

    def set_in_water(self, value: bool):
        self.in_water = value

    def draw(self, screen, x, y):
        screen.blit(self.image, (x, y))

    def remove_from_inventory(self, slot: int, quantity: int, row: int = 0):
        if not self.is_dead:
            self.inventory[row][slot]["quantity"] -= quantity
            if self.inventory[row][slot]["quantity"] <= 0:
                self.inventory[row][slot] = None

    def set_selected_slot(self, slot: int):
        if not self.is_dead:
            self.selected_inventory_slot = slot
            if not 0 <= self.selected_inventory_slot <= 8:
                self.selected_inventory_slot = 8 if self.selected_inventory_slot < 0 else 0

    def can_pick_up(self, game_map: list):
        if not self.is_dead:
            block = game_map[self.rect.y // 32 + 1][self.rect.x // 32]
            rect = pygame.Rect(self.rect.x, self.rect.y, 32, 64)
            if block.get("floating_blocks") and rect.colliderect(self.rect):
                return True, block.get("floating_blocks")
        return False, None

    def heal(self, hp: int = 1):
        if not self.is_dead:
            self.hp += hp
            if self.hp > self.max_hp:
                self.hp = self.max_hp

    def damage(self, damage: int = 0):
        if self.game_mode == 'survival':
            self.hp -= damage

            if self.hp <= 0:
                self.is_dead = True
                self.hp = 0

    def add_exp(self, exp, sounds: Sound, ):
        self.exp += exp
        sounds.play_sound('exp')
        if self.get_exp_until_next_level(self.exp, self.level + 1) <= 0:
            self.level_up(sounds)

    def level_up(self, sounds: Sound, ):
        self.level += 1
        sounds.play_sound('levelup')

    @staticmethod
    def get_experience_from_level(level: int) -> int:
        if level > 31:
            return 4.5 * (level ** 2) - 162.5 * level + 2220
        elif level > 16:
            return 2.5 * (level ** 2) - 40.5 * level + 360
        else:
            return level ** 2 + 6 * level

    def get_level_from_exp(self, exp: int = None) -> float:
        if exp is None:
            exp = self.exp
        if exp > 1508:
            res = (325 / 18) + ((2 / 9) * (exp - (54215 / 72))) ** 0.5
        elif exp > 353:
            res = (81 / 10) + ((2 / 5) * (exp - (7839 / 40))) ** 0.5
        else:
            res = (exp + 9) ** 0.5 - 3
        return res

    def get_exp_until_next_level(self, exp: int, next_level: int) -> int:
        return self.get_experience_from_level(next_level) - exp

    def get_angle_for_display(self, mouse_x, mouse_y, scroll) -> float:
        if not self.is_dead:
            rel_x, rel_y = mouse_x - (self.rect.x - scroll[0]), mouse_y - (self.rect.y - scroll[1])
            angle = (180 / math.pi) * -math.atan2(rel_y, rel_x)
            return angle
        return 1.0
